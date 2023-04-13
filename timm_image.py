# Copyright 2021 Zilliz. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import numpy
import os
from pathlib import Path
from typing import List, Union

import towhee
from towhee.operator.base import NNOperator, OperatorFlag
from towhee.types.arg import arg, to_image_color
from towhee import register
from towhee.types import Image

try:
    from towhee import accelerate
except:
    def accelerate(func):
        return func

import torch
from torch import nn

from PIL import Image as PILImage

import timm
from timm.data import create_transform, resolve_data_config
from timm.models import create_model, get_pretrained_cfg

import warnings

def script_method(fn, _rcb=None):
    return fn


def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj


import torch.jit
script_method1 = torch.jit.script_method
script1 = torch.jit.script
torch.jit.script_method = script_method
torch.jit.script = script


warnings.filterwarnings('ignore')
log = logging.getLogger('timm_op')
log.setLevel(logging.ERROR)


def torch_no_grad(f):
    def wrap(*args, **kwargs):
        with torch.no_grad():
            return f(*args, **kwargs)

    return wrap


@accelerate
class Model:
    def __init__(self, model_name, device, num_classes):
        self.device = device
        self.model = create_model(model_name, pretrained=True, num_classes=num_classes)
        self.model.eval()
        self.model.to(device)

    def __call__(self, x: torch.Tensor):
        return self.model.forward_features(x.to(self.device))


@register(output_schema=['vec'])
class TimmImage(NNOperator):
    """
    Pytorch image embedding operator that uses the Pytorch Image Model (timm) collection.
    Args:
        model_name (`str`):
            Which model to use for the embeddings.
        num_classes (`int = 1000`):
            Number of classes for classification.
        skip_preprocess (`bool = False`):
            Whether skip image transforms.
    """

    def __init__(self,
                 model_name: str = None,
                 num_classes: int = 1000,
                 skip_preprocess: bool = False,
                 device: str = None
                 ) -> None:
        super().__init__()
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = device
        self.model_name = model_name
        if self.model_name:
            self.model = Model(
                model_name=model_name,
                device=self.device,
                num_classes=num_classes
            )
            try:
                self.tfms = create_transform(
                    input_size=self.config['input_size'],
                    interpolation=self.config['interpolation'],
                    mean=self.config['mean'],
                    std=self.config['std'],
                    crop_pct=self.config['crop_pct']
                )
            except:
                self.tfms = create_transform(**resolve_data_config({}, model=self.model))
            self.skip_tfms = skip_preprocess
        else:
            log.warning('The operator is initialized without specified model.')
            pass

    @torch_no_grad
    def __call__(self, data: Union[List['towhee.types.Image'], 'towhee.types.Image']):
        if not isinstance(data, list):
            imgs = [data]
        else:
            imgs = data
        img_list = []
        for img in imgs:
            img = self.convert_img(img) if isinstance(img, numpy.ndarray) else img.convert('RGB')
            img = img if self.skip_tfms else self.tfms(img)
            img_list.append(img)
        inputs = torch.stack(img_list)
        inputs = inputs
        features = self.model(inputs)
        if isinstance(features, list):
            features = [self.post_proc(x) for x in features]
        else:
            features = self.post_proc(features)

        if isinstance(data, list):
            vecs = [list(x.detach().numpy()) for x in features] if isinstance(features, list) \
                else list(features.detach().numpy())
        else:
            vecs = [x.squeeze(0).detach().numpy() for x in features] if isinstance(features, list) \
                else features.squeeze(0).detach().numpy()
        return vecs

    @property
    def _model(self):
        return self.model.model

    @property
    def config(self):
        config = get_pretrained_cfg(self.model_name)
        return config

    @arg(1, to_image_color('RGB'))
    def convert_img(self, img: 'towhee.types.Image'):
        img = PILImage.fromarray(img.astype('uint8'), 'RGB')
        return img

    def post_proc(self, features):
        features = features.to('cpu')
        if features.dim() == 3:
            features = features[:, 0]
        if features.dim() == 4:
            global_pool = nn.AdaptiveAvgPool2d(1)
            features = global_pool(features)
            features = features.flatten(1)
        assert features.dim() == 2, f'Invalid output dim {features.dim()}'
        return features

    def save_model(self, format: str = 'pytorch', path: str = 'default'):
        if path == 'default':
            path = str(Path(__file__).parent)
            path = os.path.join(path, 'saved', format)
            os.makedirs(path, exist_ok=True)
            name = self.model_name.replace('/', '-')
            path = os.path.join(path, name)
            if format in ['pytorch', 'torchscript']:
                path = path + '.pt'
            elif format == 'onnx':
                path = path + '.onnx'
            else:
                raise AttributeError(f'Invalid format {format}.')
        dummy_input = torch.rand((1,) + self.config['input_size'])
        if format == 'pytorch':
            torch.save(self._model, path)
        elif format == 'torchscript':
            try:
                try:
                    jit_model = torch.jit.script(self._model)
                except Exception:
                    jit_model = torch.jit.trace(self._model, dummy_input, strict=False)
                torch.jit.save(jit_model, path)
            except Exception as e:
                log.error(f'Fail to save as torchscript: {e}.')
                raise RuntimeError(f'Fail to save as torchscript: {e}.')
        elif format == 'onnx':
            self._model.forward = self._model.forward_features
            try:
                torch.onnx.export(self._model.to('cpu'),
                                  dummy_input,
                                  path,
                                  input_names=['input_0'],
                                  output_names=['output_0'],
                                  opset_version=12,
                                  dynamic_axes={
                                      'input_0': {0: 'batch_size'},
                                      'output_0': {0: 'batch_size'}
                                  },
                                  do_constant_folding=True
                                  )
            except Exception as e:
                log.error(f'Fail to save as onnx: {e}.')
                raise RuntimeError(f'Fail to save as onnx: {e}.')
        # todo: elif format == 'tensorrt':
        else:
            log.error(f'Unsupported format "{format}".')
        return Path(path).resolve()

    @staticmethod
    def supported_model_names(format: str = None):
        if timm.__version__ != '0.6.12':
            log.warning('Please note that the model list is tested with timm==0.6.12, please check your timm version.')
        full_list = list(set(timm.list_models(pretrained=True)) - set([
            'coat_mini',
            'coat_tiny',
            'crossvit_9_240',
            'crossvit_9_dagger_240',
            'crossvit_15_240',
            'crossvit_15_dagger_240',
            'crossvit_15_dagger_408',
            'crossvit_18_240',
            'crossvit_18_dagger_240',
            'crossvit_18_dagger_408',
            'crossvit_base_240',
            'crossvit_small_240',
            'crossvit_tiny_240',
        ]))
        full_list.sort()
        if format in [None, 'pytorch']:
            model_list = full_list
        elif format == 'onnx':
            to_remove = [
                'bat_resnext26ts',
                'convmixer_1024_20_ks9_p14',
                'convmixer_1536_20',
                'convmixer_768_32',
                'eca_halonext26ts',
                'efficientformer_l1',
                'efficientformer_l3',
                'efficientformer_l7',
                'halo2botnet50ts_256',
                'halonet26t',
                'halonet50ts',
                'haloregnetz_b',
                'lamhalobotnet50ts_256',
                'levit_128',
                'levit_128s',
                'levit_192',
                'levit_256',
                'levit_384',
                'pvt_v2_b2_li',
                'sehalonet33ts',
                'tf_efficientnet_cc_b0_4e',
                'tf_efficientnet_cc_b0_8e',
                'tf_efficientnet_cc_b1_8e',
                'tresnet_l',
                'tresnet_l_448',
                'tresnet_m',
                'tresnet_m_448',
                'tresnet_m_miil_in21k',
                'tresnet_v2_l',
                'tresnet_xl',
                'tresnet_xl_448',
                'volo_d1_224',
                'volo_d1_384',
                'volo_d2_224',
                'volo_d2_384',
                'volo_d3_224',
                'volo_d3_448',
                'volo_d4_224',
                'volo_d4_448',
                'volo_d5_224',
                'volo_d5_448',
                'volo_d5_512'
            ]
            # assert set(to_remove).issubset(set(full_list))
            model_list = list(set(full_list) - set(to_remove))
        # todo: elif format == 'torchscript':
        # todo: elif format == 'tensorrt'
        else:
            log.error(f'Invalid format "{format}". Currently supported formats: "pytorch".')
        return model_list

    @property
    def supported_formats(self):
        if self.model_name in self.supported_model_names(format='onnx'):
            return ['onnx']
        else:
            return []

    def input_schema(self):
        return [(Image, (-1, -1, 3))]

    def output_schema(self):
        image = Image(numpy.random.randn(480, 480, 3), "RGB")
        ret = self(image)
        data_type = type(ret.reshape(-1)[0])
        return [(data_type, ret.shape)]

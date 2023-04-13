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

"""
在image_decode_cv2.py基础上修改：
cv2不支持中文路径问题
支持gif图片
"""

import logging
from typing import Union
import cv2
import imageio
import requests
import numpy as np

from towhee.operator import PyOperator
from towhee.types import Image

log = logging.getLogger()


class ImageDecodeCV2(PyOperator):
    def __init__(self, mode='BGR'):
        mode = mode.upper()
        if mode not in ['BGR', 'RGB']:
            raise RuntimeError("Mode only support BRG and RGB")
        self._mode = mode

    @staticmethod
    def _load_from_remote(image_url: str) -> np.ndarray:
        try:
            r = requests.get(image_url, timeout=(20, 20))
            if r.status_code // 100 != 2:
                log.error('Download image from %s failed, error msg: %s, request code: %s ',
                          image_url, r.text, r.status_code)
                return None
            arr = np.asarray(bytearray(r.content), dtype=np.uint8)
            return cv2.imdecode(arr, -1)
        except Exception as e:
            log.error('Download image from %s failed, error msg: %s', image_url, str(e))
            return False

    @staticmethod
    def _load_from_local(image_path: str) -> np.ndarray:
        # return cv2.imread(image_path)
        im = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
        if im is None:
            tmp = imageio.mimread(image_path)
            if tmp is not None:
                imt = np.array(tmp)
                imt = imt[0]
                im = imt[:, :, 0:3]
        return im

    @staticmethod
    def _from_bytes(image_bytes) -> np.ndarray:
        arr = np.asarray(bytearray(image_bytes), dtype=np.uint8)
        return cv2.imdecode(arr, -1)

    def __call__(self, image_data: Union[str, bytes]):
        if isinstance(image_data, bytes):
            bgr_cv_image = ImageDecodeCV2._from_bytes(image_data)
        elif image_data.startswith('http'):
            bgr_cv_image = ImageDecodeCV2._load_from_remote(image_data)
        else:
            bgr_cv_image = ImageDecodeCV2._load_from_local(image_data)

        if bgr_cv_image is None:
            err = 'Read image %s failed' % image_data
            log.error(err)
            raise RuntimeError(err)

        if self._mode == 'BGR':
            return Image(bgr_cv_image, 'BGR')
        rgb_cv_image = cv2.cvtColor(bgr_cv_image, cv2.COLOR_BGR2RGB)
        return Image(rgb_cv_image, 'RGB')

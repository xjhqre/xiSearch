import configparser
import os
from glob import glob
from towhee.dc2 import pipe, ops
import image_decode_custom
import timm_image

'''
towhee管道
'''

image_embedding = timm_image.TimmImage(model_name='resnet50')
image_decode_custom = image_decode_custom.ImageDecodeCV2()
configFile = 'config.ini'
# 创建配置文件对象
config = configparser.ConfigParser()
# 读取文件
config.read(configFile, encoding='utf-8')
allowTypes = config.get("SETTINGS", "allowTypes")


# 加载图片路径
def load_image(folderPath):
    for filePath in glob(folderPath):
        if os.path.splitext(filePath)[1] in allowTypes:
            yield filePath


# Embedding pipeline
p_embed = (
    pipe.input('src', 'self')
    # 传入src，输出img_path
    .flat_map('src', 'img_path', load_image)
    # 传入img_path，输出img
    # .map('img_path', 'img', ops.image_decode())
    .map('img_path', 'img', image_decode_custom)
    # 传入img，输出vec
    .map('img', 'vec', image_embedding)
    # .map('img', 'vec', ops.image_embedding.timm(model_name='resnet50'))
)

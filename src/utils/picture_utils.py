import base64
import imghdr
import os

from PIL import Image

from src.config import config


def get_image_mime_type(file_path):
    return imghdr.what(file_path)


def generateBase64(img_path_list):
    base64_list = []
    for img_path in img_path_list:
        mime_type = get_image_mime_type(img_path)
        if mime_type is None:
            mime_type = "jpeg"
        # 打开图片文件
        with Image.open(img_path) as im:
            # 获取文件名
            file_name = os.path.basename(img_path)
            # 生成缩略图
            im.thumbnail((400, 400))

            # 保存缩略图
            if not os.path.exists(config.project_path + 'img/'):
                # 如果目录不存在则创建
                os.makedirs(config.project_path + 'img/')
            im.save(config.project_path + 'img/' + file_name)

        with open(config.project_path + 'img/' + file_name, 'rb') as f:
            base64_data = "data:image/" + mime_type + ";base64," + base64.b64encode(f.read()).decode('utf-8')

        # 使用完后删除缩略图
        os.remove(config.project_path + 'img/' + file_name)

        # 打印Base64编码
        base64_list.append(base64_data)

    return base64_list

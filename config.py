import configparser
import os

configFile = 'config.ini'
# 创建配置文件对象
config = configparser.ConfigParser()
# 读取文件
config.read(configFile, encoding='utf-8')

# 图片库地址
gallery_path = config.get("SETTINGS", "gallery_path")

# 特征向量地址
feature_path = os.getcwd() + "/feature/"
if not os.path.exists(feature_path):  # 判断文件夹是否存在
    os.mkdir(feature_path)  # 创建文件夹

# 搜索的图片地址
search_img_path = ""

# 允许的图片类型
allow_types = [".jpg", ".jpeg", ".gif", ".png", ".JPG", ".JPEG", ".GIF", ".PNG"]

# batch大小
batch_size = int(config.get("SETTINGS", "batch_size"))


def update_gallery_path(value):
    config.read(configFile, encoding='utf-8')
    try:
        config.add_section("SETTINGS")
    except configparser.DuplicateSectionError:
        pass

    config.set("SETTINGS", "gallery_path", value)

"""
JavaScript调用python接口
"""

from src.config.config import config_instance
from src.log.log import log
from src.utils import feature_extractor
from src.utils.feature_extractor import fe
from src.utils.picture_utils import generateBase64


class Api:

    def load_configuration_file(self):
        """
        读取配置文件
        :return:
        """
        response = {
            'feature_path': config_instance.feature_path,
            'result_count': config_instance.result_count,
            'gallery_path': config_instance.gallery_path
        }
        return response

    def update_feature_path(self, new_feature_path):
        """
        更新特征向量存储地址配置
        :param new_feature_path:
        :return:
        """
        config_instance.feature_path = new_feature_path

    def update_result_count(self, new_result_count):
        """
        更新搜索图片数量配置
        :param new_result_count:
        :return:
        """
        config_instance.result_count = new_result_count

    def update_gallery_path(self, new_gallery_path):
        """
        更新图片库地址
        :param new_gallery_path:
        :return:
        """
        config_instance.gallery_path = new_gallery_path

    def feature_extraction(self, img_folder_path):
        """
        提取特征图片
        :return:
        """
        fe.extract_batch(img_folder_path)

    def get_extraction_log(self):
        """
        获取提取日志
        :return:
        """
        response = {
            'extract_log': log.extract_log
        }
        return response

    def search_images(self, search_img_path):
        """
        搜索图片
        :return:
        """
        img_path_list = feature_extractor.search(search_img_path)
        response = {
            'img_path_list': img_path_list,
            'base64_list': generateBase64(img_path_list)
        }
        return response


js_api = Api()

if __name__ == '__main__':
    js_api.load_configuration_file()

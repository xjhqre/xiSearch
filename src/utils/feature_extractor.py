import glob
import os
import pickle
import time

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

from src.config.config import config_instance
from src.exception.my_base_exception import MyBaseException
from src.exception.no_feature_file_exception import NoFeatureFileException
from src.exception.no_feature_path_exception import NoFeaturePathException
from src.log.log import log


def image_process(img_path):
    """
    加载、调整大小和转换图像为RGB格式

    Args:
    img_path (str): 图像文件的路径

    Returns:
    PIL.Image: 调整大小并转换为RGB格式后的图像对象
    """
    img = image.load_img(img_path, target_size=(224, 224))
    img = img.resize((224, 224))
    img = img.convert('RGB')
    return img


def dump(img_name_list, img_feature_list):
    """
    将图像名称列表和图像特征列表保存到文件中

    Args:
    img_name_list (list): 包含图像名称的列表
    img_feature_list (list): 包含图像特征的列表

    Returns:
    None
    """
    if not os.path.exists(config_instance.feature_path):
        os.makedirs(config_instance.feature_path)
    with open(config_instance.feature_path + os.sep + str(int(time.time())) + ".pickle", 'wb') as fOut:
        pickle.dump((img_name_list, img_feature_list), fOut)


def get_file_paths(img_folder_path, batch_size):
    """
    获取图像文件夹中的文件路径列表，按批次大小返回

    Args:
    img_folder_path (str): 图像文件夹的路径
    batch_size (int): 批次大小，用于控制每个批次返回的文件路径数量

    Yields:
    list: 包含指定批次数量的图像文件路径的列表

    Returns:
    None
    """
    img_path_list = glob.glob(os.path.join(img_folder_path, "*"))
    for i in range(0, len(img_path_list), batch_size):
        yield img_path_list[i:i + batch_size]


def search(query_img_path, k=None):
    """
    搜索相似图像

    Args:
    query_img_path (str): 查询图像文件的路径
    k (int, optional): 返回最相似的前k个图像，默认为None，如果为None，则使用配置中的默认值

    Returns:
    list: 包含最相似的前k个图像文件路径的列表
    """
    # 默认参数值是在函数定义时计算的，而不是在运行时计算的
    if k is None:
        k = int(config_instance.result_count)

    feature_path = config_instance.feature_path
    if not os.path.exists(feature_path):
        raise NoFeaturePathException

    query_img_feature = fe.extract(query_img_path)  # 搜索图片特征

    similarities_dict = {}  # 用于存储图像路径和对应的相似度

    feature_path_list = glob.glob(os.path.join(feature_path, "*"))
    if len(feature_path_list) == 0:
        raise NoFeatureFileException

    # 从每个特征文件中提取出最相似的k个图片
    for feature_path in feature_path_list:
        with open(feature_path, 'rb') as fIn:
            name_list, feature_list = pickle.load(fIn)
            similarities = cosine_similarity([query_img_feature], feature_list)[0]  # 相似度 ndarray (xxx,)
            for i, img_name in enumerate(name_list):
                similarities_dict[img_name] = similarities[i]

    # 根据相似度降序排序，并返回前k个最相似的图像路径
    sorted_similarities = sorted(similarities_dict.items(), key=lambda x: x[1], reverse=True)
    return [img_path for img_path, _ in sorted_similarities[:k]]


class FeatureExtractor:
    def __init__(self):
        self.model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

    def extract(self, img_path):
        """
        提取图像特征

        Args:
        self: 对象本身
        img_path (str): 图像文件的路径

        Returns:
        numpy.ndarray: 包含提取的图像特征的一维数组
        """
        img = image_process(img_path)
        x = image.img_to_array(img)  # 将图像转换为numpy数组
        x = np.expand_dims(x, axis=0)  # 在第0轴上扩展维度
        x = preprocess_input(x)
        feature = self.model.predict(x)  # 使用模型提取特征
        return feature.flatten()  # 返回扁平化的特征数组

    def extract_batch(self, img_folder_path, batch_size=32):
        """
        批量提取
        :param img_folder_path: 图片文件夹路径
        :param batch_size: batch大小
        :return:
        """
        if not os.path.isdir(img_folder_path):
            raise MyBaseException("图片文件夹路径错误")

        cnt = 0  # 图片计数
        time_start = time.time()
        # 获取图片路径生成器
        img_path_list_generator = get_file_paths(img_folder_path, batch_size)

        img_path_batch = []  # 每1024个特征保存一次
        img_feature_batch = []  # 每1024个特征保存一次
        log.extract_log = "开始提取！\n"

        for img_path_list in img_path_list_generator:
            # 过滤掉非图片类型的文件
            img_path_list = [name for name in img_path_list if
                             os.path.splitext(name)[1] in config_instance.allow_types]

            # 创建一个空的数组用于存储图像数据
            batch_images = np.zeros(
                (len(img_path_list), 224, 224, 3))

            for i, img_path in enumerate(img_path_list):
                img = image_process(img_path)
                x = image.img_to_array(img)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)
                batch_images[i % len(img_path_list)] = x  # 将图像添加到批次数组中

            # 当达到批量处理大小时或者是最后一张图像时进行处理
            feature_ndarray = self.model.predict(batch_images)  # 执行特征提取, (10, 2048)
            feature_list = [np.array(feature) for feature in feature_ndarray]  # list<ndarray>
            img_path_batch.extend(img_path_list)
            img_feature_batch.extend(feature_list)

            cnt += len(img_path_list)
            time_process = time.time()
            time_use = time_process - time_start
            log.extract_log += "已提取图片数量：{}, 耗时：{} 秒\n".format(cnt, time_use)

            # 每1024个特征保存一次
            if len(img_path_batch) >= 1024:
                dump(img_path_batch, img_feature_batch)
                img_path_batch = []
                img_feature_batch = []

        # 保存剩余的特征
        dump(img_path_batch, img_feature_batch)

        time_end = time.time()
        time_sum = time_end - time_start
        log.extract_log += "提取结束，提取成功图片: {} 张, 总耗时: {} 秒\n".format(
            cnt, time_sum)


fe = FeatureExtractor()

if __name__ == '__main__':
    # result = search("F:\\ACG\\壁纸\\(14).jpg")
    # print(result)
    fe.extract_batch("F:\\ACG\\壁纸")
    # fe.extract("F:\\ACG\\新建文件夹\\63-1Z61Q45G4Z7.png")
    # print(list(glob.glob(config_instance.get_feature_path + os.sep + "*")))

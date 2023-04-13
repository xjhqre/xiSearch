import configparser
import pickle
from glob import glob

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from pipeline import p_embed

'''
图片搜索线程类
'''

# ----------------------- 全局变量 --------------------------- #
configFile = 'config.ini'
# 创建配置文件对象
config = configparser.ConfigParser()
# 读取文件
config.read(configFile, encoding='utf-8')
featurePath = config.get("SETTINGS", "featurePath")


# 余弦相似度计算查询，入参 查询图片的特征向量，出参：最相似30张图片的绝对路径
def cosine_similarity_query(vec1):
    vec1 = vec1[::2]
    featureFilePathList = glob(featurePath + '/*')  # 特征文件路径列表
    # 每次读取一个特征文件，最多包含1000个特征向量，防止一次性载入导致内存过大
    similarity_list = []  # 向量距离数组
    img_path_list = []  # 图片路径数组
    for i, featureFilePath in enumerate(featureFilePathList):
        pkl = pickle.load(open(featureFilePath, 'rb'))
        features = []  # 存储特征向量，最大size为1000
        img_paths = []  # 存储图片路径，最大size为1000
        for v in pkl.values():
            features.append(v['feature'])
            img_paths.append(v['path'])
        feature_ndarry = np.array(features)
        img_paths_ndarry = np.array(img_paths)
        dists = []
        for vec2 in feature_ndarry:
            cos_sim = vec1.dot(vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            dists.append(cos_sim)
        dists = np.linalg.norm(feature_ndarry - vec1, axis=1)  # 1000个距离值
        ids = np.argsort(dists)[:30]  # 从dists数组中选择距离最近的30个向量，并返回这些向量在feature_ndarry中的索引
        dists = dists[ids]  # 1000张图片里30张最相似图片的距离
        img_paths_ndarry = img_paths_ndarry[ids]  # 1000张图片里30张最相似图片的路径
        similarity_list.extend(list(dists))
        img_path_list.extend(list(img_paths_ndarry))
    similarity_list = np.array(similarity_list)
    img_path_list = np.array(img_path_list)
    index_list = np.argsort(similarity_list)[:30]  # 所有特征文件中最相似的30个向量的下标
    img_path_list = img_path_list[index_list]  # 所有图片中最相似的30张图片路径
    return img_path_list


class ImageSearchClass(QThread):
    completeSignal = pyqtSignal(np.ndarray)  # 搜素开始信号
    imgPathEdit = ""

    # Search pipeline
    p_search_pre = (
        p_embed.map('vec', 'search_res', cosine_similarity_query)
    )
    # 输出 search_res
    p_search = p_search_pre.output('search_res')

    def __init__(self):
        super(ImageSearchClass, self).__init__()

    def run(self):
        img_path_list = self.p_search(self.imgPathEdit, self)
        self.completeSignal.emit(img_path_list.get()[0])

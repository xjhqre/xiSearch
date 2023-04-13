import glob
import pickle

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from feature_extractor import fe


class ImageSearch(QThread):
    completeSignal = pyqtSignal(np.ndarray)  # 搜素完成信号
    featurePath = ''
    imgPathEdit = ""

    def __init__(self, featurePath):
        super(ImageSearch, self).__init__()
        self.featurePath = featurePath

    def do_search(self, searchImgPath):
        try:
            feature = fe.execute(searchImgPath)
            feature = np.array(feature)
        except Exception as e:
            print("出现异常：" + str(e))
        else:
            total_similarity_list = []  # 总相似度数组
            total_img_name_list = []  # 总图片名称数组
            featureFilePathList = glob.glob(self.featurePath + '/*')  # 特征文件路径列表
            # 每次读取一个特征文件，最多包含1000个特征向量，防止一次性载入导致内存过大
            for i, featureFilePath in enumerate(featureFilePathList):
                pkl = pickle.load(open(featureFilePath, 'rb'))
                feature_list = []  # 特征向量数组
                img_name_list = []  # 存储图片名称
                for v in pkl.values():
                    feature_list.append(v['feature'])
                    img_name_list.append(v['name'])
                feature_ndarray = np.array(feature_list)
                img_name_ndarray = np.array(img_name_list)
                similarity_list = []  # 一个特征向量文件中的余弦相似度数组，值域为 [-1, 1]，值越小越相似
                for vec2 in feature_ndarray:
                    cos_sim = feature.dot(vec2) / (np.linalg.norm(feature) * np.linalg.norm(vec2))
                    similarity_list.append(0 - cos_sim)
                similarity_ndarray = np.array(similarity_list)
                ids = np.argsort(similarity_ndarray)[:30]  # 从 similarity_ndarray 中选择30个最小的值的索引
                similarity_ndarray = similarity_ndarray[ids]  # 一个特征向量文件中最小的30个相似度
                img_name_ndarray = img_name_ndarray[ids]  # 一个特征向量文件中最相似的30张图片的名称
                total_similarity_list.extend(list(similarity_ndarray))
                total_img_name_list.extend(list(img_name_ndarray))
            total_similarity_ndarray = np.array(total_similarity_list)
            total_img_name_ndarray = np.array(total_img_name_list)
            index_list = np.argsort(total_similarity_ndarray)[:30]  # 所有特征文件中最小的30个相似度的下标
            total_img_name_ndarray = total_img_name_ndarray[index_list]  # 所有特征文件中最相似的30张图片名称
            return total_img_name_ndarray

    def run(self):
        img_path_list = self.do_search(self.imgPathEdit)
        self.completeSignal.emit(img_path_list)

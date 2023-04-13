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
            featureFilePathList = glob.glob(self.featurePath + '/*')  # 特征文件路径列表
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
                    cos_sim = feature.dot(vec2) / (np.linalg.norm(feature) * np.linalg.norm(vec2))
                    dists.append(cos_sim)
                dists = np.linalg.norm(feature_ndarry - feature, axis=1)  # 1000个距离值
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

    def run(self):
        img_path_list = self.do_search(self.imgPathEdit)
        self.completeSignal.emit(img_path_list)

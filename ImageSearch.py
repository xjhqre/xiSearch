import glob
import pickle

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from feature_extractor import fe


class ImageSearch(QThread):
    completeSignal = pyqtSignal(np.ndarray)  # 搜素完成信号
    featurePath = ''
    imgPathEdit = ""

    def __init__(self, feature_path):
        super(ImageSearch, self).__init__()
        self.featurePath = feature_path

    def do_search(self, search_img_path):
        try:
            feature = fe.execute(search_img_path)
            feature = np.array(feature)
        except Exception as e:
            print("出现异常：" + str(e))
        else:
            total_similarity_list = []  # 总相似度数组
            total_img_name_list = []  # 总图片名称数组
            feature_file_path_list = glob.glob(self.featurePath + '/*')  # 特征文件路径列表
            # 每次读取一个特征文件，最多包含1000个特征向量，防止一次性载入导致内存过大
            for i, feature_file_path in enumerate(feature_file_path_list):
                pkl = pickle.load(open(feature_file_path, 'rb'))
                feature_list = []  # 特征向量数组
                img_name_list = []  # 存储图片名称
                for v in pkl.values():
                    feature_list.append(np.array(v['feature']))
                    img_name_list.append(v['name'])
                feature_ndarray = np.array(feature_list)
                img_name_ndarray = np.array(img_name_list)
                similarity_ndarray = np.dot(feature_ndarray, feature) / (np.linalg.norm(feature_ndarray, axis=1) * np.linalg.norm(feature))
                ids = np.argsort(similarity_ndarray)[::-1][:30]
                similarity_ndarray = similarity_ndarray[ids]
                img_name_ndarray = img_name_ndarray[ids]
                total_similarity_list.extend(list(similarity_ndarray))
                total_img_name_list.extend(list(img_name_ndarray))
            total_similarity_ndarray = np.array(total_similarity_list)
            total_img_name_ndarray = np.array(total_img_name_list)
            index_list = np.argsort(total_similarity_ndarray)[::-1][:30]
            total_img_name_ndarray = total_img_name_ndarray[index_list]
            return total_img_name_ndarray

    def run(self):
        img_path_list = self.do_search(self.imgPathEdit)
        self.completeSignal.emit(img_path_list)

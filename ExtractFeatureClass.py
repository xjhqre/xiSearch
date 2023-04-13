import configparser
import os
import pickle
import time
from glob import glob

from PyQt5.QtCore import QThread, pyqtSignal

import timm_image
import image_decode_custom

'''
特征提取线程类
'''

image_embedding = timm_image.TimmImage(model_name='resnet50')
image_decode = image_decode_custom.ImageDecodeCV2()
total = 0  # 文件目录下的支持的图片总数
cnt = 0  # 当前提取图片的索引
featureFileCnt = 1  # 生成特征文件的索引
img_pkl = {}  # 特征向量字典
configFile = 'config.ini'
# 创建配置文件对象
config = configparser.ConfigParser()
# 读取文件
config.read(configFile, encoding='utf-8')
allowTypes = config.get("SETTINGS", "allowTypes")
pickleStorage = 1000  # 设置每个pickle文件存储多少特征向量


# 提取特征线程
class ExtractFeatureClass(QThread):
    processSignal = pyqtSignal(int)  # 进度信号
    galleryPath = config.get("SETTINGS", "galleryPath")
    featurePath = config.get("SETTINGS", "featurePath")

    def __init__(self):
        super(ExtractFeatureClass, self).__init__()

    # 保存为pickle文件
    def save_pickle(self, filePath, vec):
        vec = vec[::2]  # 特征向量，resnet50提取的图片向量维度是2048，es7.4版本支持的最大维度是1024
        img_v = {'path': filePath, 'feature': vec}
        global cnt
        img_pkl[cnt] = img_v
        cnt += 1
        self.processSignal.emit(int(cnt * 100 / total))
        print("当前图片：" + filePath + " ---> " + str(cnt))
        if cnt % pickleStorage == 0:
            # 保存特征到本地
            global featureFileCnt
            pickle.dump(img_pkl, open(self.featurePath + '\\img_pkl_' + str(featureFileCnt), 'wb'))
            featureFileCnt += 1
            img_pkl.clear()

    # # Insert pipeline
    # p_insert = (
    #     # 传入('img_path', 'vec')，无输出
    #     p_embed.map(('self', 'img_path', 'vec'), (), save_pickle)
    #     .output()
    # )

    def extract(self, galleryPath):
        for path in glob(galleryPath):
            if os.path.splitext(path)[1] not in allowTypes:
                continue
            img = image_decode(path)
            vec = image_embedding(img)
            self.save_pickle(path, vec)

    def run(self):
        time_start = time.time()  # 记录开始时间
        trainPath = glob(self.galleryPath)  # 被检索的图片路径
        global total
        total = len(trainPath)
        # 获取支持的图片文件总数
        for i, image in enumerate(trainPath):
            (filename, extension) = os.path.splitext(image)
            if extension not in allowTypes:
                total -= 1

        self.extract(self.galleryPath)

        global featureFileCnt
        if img_pkl != {}:
            pickle.dump(img_pkl, open(self.featurePath + '\\img_pkl_' + str(featureFileCnt), 'wb'))
            featureFileCnt += 1
            img_pkl.clear()

        time_end = time.time()  # 记录结束时间
        time_sum = time_end - time_start
        print("提取特征文件耗时：" + str(time_sum) + " 秒")

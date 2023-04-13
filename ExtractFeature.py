import glob
import os
import pickle
import time

from PyQt5.QtCore import QThread, pyqtSignal

from feature_extractor import fe

total = 0  # 文件目录下的支持的图片总数
cnt = 0  # 当前提取图片的索引
featureFileCnt = 1  # 生成特征文件的索引
img_pkl = {}  # 特征向量字典
errorImg = []  # 出错文件集合
pickleStorage = 1000  # 设置每个pickle文件存储多少特征向量


# 提取特征线程
class ExtractFeature(QThread):
    processSignal = pyqtSignal(int)  # 进度信号
    galleryPath = ''
    featurePath = ''
    allowTypes = []

    def __init__(self, galleryPath, featurePath, allowTypes):
        super(ExtractFeature, self).__init__()
        self.galleryPath = galleryPath
        self.featurePath = featurePath
        self.allowTypes = allowTypes

    def extract(self, galleryPath):
        global featureFileCnt, cnt, total
        imagePathList = glob.glob(galleryPath)  # 被检索的图片路径
        total = len(imagePathList)
        # 获取支持的图片文件总数
        for i, imgPath in enumerate(imagePathList):
            (filename, extension) = os.path.splitext(imgPath)
            img_name = os.path.basename(imgPath)
            if extension not in self.allowTypes:
                total -= 1
                continue
            try:
                feature = fe.execute(imgPath)
            except Exception as e:
                print("出现异常：" + str(e))
                total -= 1
                errorImg.append(imgPath)
            else:
                img_v = {'name': img_name, 'feature': feature}
                img_pkl[cnt] = img_v
                cnt += 1
                self.processSignal.emit(int(cnt * 100 / total))
                print("当前图片：" + imgPath + " ---> " + str(cnt))
                if cnt % pickleStorage == 0:
                    # 保存特征到本地
                    pickle.dump(img_pkl, open(self.featurePath + '\\img_pkl_' + str(featureFileCnt), 'wb'))
                    featureFileCnt += 1
                    img_pkl.clear()
        if img_pkl != {}:
            pickle.dump(img_pkl, open(self.featurePath + '\\img_pkl_' + str(featureFileCnt), 'wb'))
            featureFileCnt += 1
            img_pkl.clear()

        # 打印失败文件信息
        if len(errorImg) != 0:
            print("Error: 提取失败的图片路径：")
            for image in errorImg:
                print(image)

    def run(self):
        time_start = time.time()  # 记录开始时间
        self.extract(self.galleryPath + "/*")
        time_end = time.time()  # 记录结束时间
        time_sum = time_end - time_start
        print("提取特征文件耗时：" + str(time_sum) + " 秒")

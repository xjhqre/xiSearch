import glob
import os
import pickle
import sys
import time

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
import configparser
import mainUI
from feature_extractor import FeatureExtractor

allowTypes = [".jpg", ".jpeg", ".gif", ".png", ".JPG", ".JPEG", ".GIF", ".PNG"]
fe = FeatureExtractor()  # 特征提取器
configFile = 'config.ini'
# 创建配置文件对象
config = configparser.ConfigParser()
# 读取文件
config.read(configFile, encoding='gbk')
galleryPath = config.get("SETTINGS", "galleryPath")
featurePath = config.get("SETTINGS", "featurePath")


class MainWindow(mainUI.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.extractFeature = ExtractFeatureThread()
        self.extractFeature.processSignal.connect(self.progressBarEvent)
        self.galleryPathEdit.setText(galleryPath)
        self.featurePathEdit.setText(featurePath)
        self.imgsearchPageButton.clicked.connect(self.display1)
        self.excutePageButton.clicked.connect(self.display2)
        # 搜索按钮点击事件
        self.searchButton.clicked.connect(self.searchImgEvent)
        # 提取特征按钮点击事件
        self.excuteButton.clicked.connect(self.extractFeatureEvent)
        # # 加载特征按钮点击事件
        # self.loadFeatureButton.clicked.connect(self.loadFeatureButtonEvent)
        # 图片库输入框改变事件
        self.galleryPathEdit.textChanged.connect(self.galleryPathFocusOutEvent)
        # 特征文件输入框文本改变事件
        self.featurePathEdit.textChanged.connect(self.featurePathFocusOutEvent)

    def display1(self):
        self.stackedWidget.setCurrentIndex(0)

    def display2(self):
        self.stackedWidget.setCurrentIndex(1)

    # 点击搜索图片按钮事件
    def searchImgEvent(self):

        if self.featurePathEdit.toPlainText() == "":
            QMessageBox.information(self, '提示', '请先设置特征文件路径', QMessageBox.Yes)
            return
        if self.imgPathEdit.toPlainText() == "":
            QMessageBox.information(self, '提示', '请设置查询图片', QMessageBox.Yes)
            return
        self.loadingMsgLabel.setText("正在搜索图片，请稍后")
        self.loadingMsgLabel.setHidden(False)
        self.imageListWidgetUI.widget_2.setHidden(True)

        dists_list = []  # 向量距离数组
        img_path_list = []  # 图片路径数组

        # 解析传入图片特征并匹配
        query = fe.execute(self.imgPathEdit.toPlainText())
        featureFilesPath = glob.glob(featurePath + '/*')  # 被检索的图片路径
        # 每次读取一个特征文件，最多包含1000个特征向量，防止一次性载入导致内存过大
        for i, featureFilePath in enumerate(featureFilesPath):
            pkl = pickle.load(open(featureFilePath, 'rb'))
            features = []  # 存储特征向量，最大size为1000
            img_paths = []  # 存储图片路径，最大size为1000
            for v in pkl.values():
                features.append(v['feature'])
                img_paths.append(v['path'])
            feature_ndarry = np.array(features)
            img_paths_ndarry = np.array(img_paths)
            dists = np.linalg.norm(feature_ndarry - query, axis=1)  # 1000个距离值
            ids = np.argsort(dists)[:30]  # 从小到大排序，取前30个，ids为最小30个值的下标
            dists = dists[ids]  # 1000张图片里30张最相似图片的距离
            img_paths_ndarry = img_paths_ndarry[ids]  # 1000张图片里30张最相似图片的路径
            dists_list.extend(list(dists))
            img_path_list.extend(list(img_paths_ndarry))
        dists_list = np.array(dists_list)
        img_path_list = np.array(img_path_list)
        index_list = np.argsort(dists_list)[:30]  # 所有特征文件中最相似的30个向量的下标
        img_path_list = img_path_list[index_list]  # 所有图片中最相似的30张图片路径
        self.imageListWidgetUI.load_images(img_path_list)
        self.imageListWidgetUI.widget_2.setHidden(False)
        self.loadingMsgLabel.setHidden(True)

    # 提取图片库特征事件
    def extractFeatureEvent(self):
        if galleryPath == "":
            QMessageBox.information(self, '提示', '请设置图片库路径', QMessageBox.Yes)
            return
        elif featurePath == "":
            QMessageBox.information(self, '提示', '请设置特征文件保存路径', QMessageBox.Yes)
            return
        self.extractFeature.start()

    # 图片库输入文本框改变事件
    def galleryPathFocusOutEvent(self):
        # print(self.galleryPathEdit.toPlainText())
        config.read(configFile)
        try:
            config.add_section("SETTINGS")
        except configparser.DuplicateSectionError:
            pass

        config.set("SETTINGS", "galleryPath", self.galleryPathEdit.toPlainText())
        global galleryPath
        galleryPath = self.galleryPathEdit.toPlainText()

        with open(configFile, "w") as config_file:
            config.write(config_file)

    # 特征文件输入文本框改变事件
    def featurePathFocusOutEvent(self):
        # print(self.featurePathEdit.toPlainText())
        config.read(configFile)
        try:
            config.add_section("SETTINGS")
        except configparser.DuplicateSectionError:
            pass

        config.set("SETTINGS", "featurePath", self.featurePathEdit.toPlainText())
        global featurePath
        featurePath = self.featurePathEdit.toPlainText()

        with open(configFile, "w") as config_file:
            config.write(config_file)

    # 提取特征进度条进度
    def progressBarEvent(self, num):
        self.progressBar.setValue(num)
        if num == 100:
            QMessageBox.information(self, '提示', '特征提取完成', QMessageBox.Yes)


# 提取特征线程
class ExtractFeatureThread(QThread):
    processSignal = pyqtSignal(int)  # 进度信号

    def __init__(self):
        super(ExtractFeatureThread, self).__init__()

    def run(self):
        time_start = time.time()  # 记录开始时间
        trainPath = glob.glob(galleryPath)  # 被检索的图片路径
        total = len(trainPath)
        featureFileCnt = 1
        cnt = 1
        img_pkl = {}
        errorImg = []  # 出错文件集合
        for i, image in enumerate(trainPath):
            # image：F:/ACG/头像\1a2221f1f81fe57046ce944efd3306b3.jpg
            (filename, extension) = os.path.splitext(image)

            if extension == '.ini':
                total -= 1
                continue
            elif extension not in allowTypes:
                print("格式出错：" + image)
                total -= 1
                errorImg.append(image)
                continue

            try:
                feature = fe.execute(image)  # 提取特征向量
            except Exception as e:
                print("出现异常：" + str(e))
                total -= 1
                errorImg.append(image)
            else:
                img_v = {'path': image, 'feature': feature}
                img_pkl[cnt] = img_v
                self.processSignal.emit(int(cnt * 100 / total))
                print("当前图片：" + image + " ---> " + str(cnt))
                cnt += 1
                if (i + 1) % 1000 == 0:
                    # 保存特征到本地
                    pickle.dump(img_pkl, open(featurePath + '\\img_pkl_' + str(featureFileCnt), 'wb'))
                    featureFileCnt += 1
                    img_pkl.clear()
        if img_pkl != {}:
            pickle.dump(img_pkl, open(featurePath + '\\img_pkl_' + str(featureFileCnt), 'wb'))
            featureFileCnt += 1
            img_pkl.clear()

        # 打印失败文件信息
        if len(errorImg) != 0:
            print("Error: 提取失败的图片路径：")
            for image in errorImg:
                print(image)

        time_end = time.time()  # 记录结束时间
        time_sum = time_end - time_start
        print("提取特征文件耗时：" + str(time_sum) + " 秒")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pages_window = MainWindow()
    pages_window.show()

    # 关闭程序，释放资源
    sys.exit(app.exec_())

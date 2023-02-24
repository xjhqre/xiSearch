import glob
import os
import pickle
import sys

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
import configparser
import mainUI
from feature_extractor import FeatureExtractor

allowTypes = [".jpg", ".jpeg", ".gif", ".png", ".JPG", ".JPEG", ".GIF", ".PNG"]
features = []  # 图片特征向量集合
feature_ndarry = None
img_paths = []  # 图片路径集合
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
        # 加载特征按钮点击事件
        self.loadFeatureButton.clicked.connect(self.loadFeatureButtonEvent)
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
        global feature_ndarry, img_paths

        if self.featurePathEdit.toPlainText() == "":
            QMessageBox.information(self, '提示', '请先设置特征文件路径', QMessageBox.Yes)
            return
        if feature_ndarry is None:
            QMessageBox.information(self, '提示', '请先加载特征文件', QMessageBox.Yes)
            return
        if self.imgPathEdit.toPlainText() == "":
            QMessageBox.information(self, '提示', '请设置查询图片', QMessageBox.Yes)
            return
        self.loadingMsgLabel.setText("正在搜索图片，请稍后")
        self.loadingMsgLabel.setHidden(False)
        self.imageListWidgetUI.widget_2.setHidden(True)

        # 解析传入图片特征并匹配
        query = fe.execute(self.imgPathEdit.toPlainText())
        dists = np.linalg.norm(feature_ndarry - query, axis=1)  # L2 distances to features
        ids = np.argsort(dists)[:30]  # Top 30 results

        self.imageListWidgetUI.load_images(ids, img_paths)
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

    # 加载特征按钮点击事件
    def loadFeatureButtonEvent(self):
        if featurePath == "":
            QMessageBox.information(self, '提示', '请设置特征文件路径', QMessageBox.Yes)
            return
        global features, feature_ndarry, img_paths
        try:
            img_pkl = pickle.load(open(featurePath, 'rb'))
            for value in img_pkl.values():
                features.append(value['feature'])
                img_paths.append(value['path'])
            feature_ndarry = np.array(features)
            QMessageBox.information(self, '提示', '加载完成', QMessageBox.Yes)
        except Exception as e:
            QMessageBox.information(self, '提示', '请输入正确的路径', QMessageBox.Yes)
            return

    # 图片库输入框失去焦点事件
    def galleryPathFocusOutEvent(self):
        print(self.galleryPathEdit.toPlainText())
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

    # 特征文件输入框失去焦点事件
    def featurePathFocusOutEvent(self):
        print(self.featurePathEdit.toPlainText())
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
        trainPath = glob.glob(galleryPath)  # 被检索的图片路径
        total = len(trainPath)
        cnt = 0
        img_pkl = {}
        errorImg = []  # 出错文件集合
        for i, image in enumerate(trainPath):
            # image：F:/ACG/头像\1a2221f1f81fe57046ce944efd3306b3.jpg
            (filename, extension) = os.path.splitext(image)

            if extension == '.ini':
                total -=1
                continue
            elif extension not in allowTypes:
                print("格式出错：" + image)
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
                cnt += 1
                self.processSignal.emit(int((cnt)*100 / total))
                print("当前图片：" + image + " ---> " + str(cnt))

        # 打印失败文件信息
        if len(errorImg) != 0:
            print("Error: 提取失败的图片路径：")
            for image in errorImg:
                print(image)

        # 保存特征到本地
        pickle.dump(img_pkl, open(featurePath, 'wb'))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 初始化
    try:
        img_pkl = pickle.load(open(featurePath, 'rb'))
        for value in img_pkl.values():
            features.append(value['feature'])
            img_paths.append(value['path'])
        feature_ndarry = np.array(features)
    except Exception:
        pass

    pages_window = MainWindow()
    pages_window.show()

    # 关闭程序，释放资源
    sys.exit(app.exec_())

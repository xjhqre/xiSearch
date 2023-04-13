import configparser
import os
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox

import mainUI
from ExtractFeatureClass import ExtractFeatureClass
from ImageSearchClass import ImageSearchClass

'''
主启动类
'''

# ----------------------- 全局变量 --------------------------- #
configFile = 'config.ini'
# 创建配置文件对象
config = configparser.ConfigParser()
# 读取文件
config.read(configFile, encoding='utf-8')
galleryPath = config.get("SETTINGS", "galleryPath")
featurePath = config.get("SETTINGS", "featurePath")


class MainWindow(mainUI.Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.extractFeature = ExtractFeatureClass()
        self.extractFeature.processSignal.connect(self.progressBarEvent)
        self.imgSearchClass = ImageSearchClass()
        self.imgSearchClass.completeSignal.connect(self.searchCompleteEvent)
        self.galleryPathEdit.setText(galleryPath)
        self.featurePathEdit.setText(featurePath)
        # 图片搜索按钮切换页面事件
        self.imgsearchPageButton.clicked.connect(self.display1)
        # 特征抽取按钮切换页面事件
        self.excutePageButton.clicked.connect(self.display2)
        # 搜索按钮点击事件
        self.searchButton.clicked.connect(self.searchImgEvent)
        # 提取特征按钮点击事件
        self.excuteButton.clicked.connect(self.extractFeatureEvent)
        # 图片库输入框改变事件
        self.galleryPathEdit.textChanged.connect(self.galleryPathFocusOutEvent)
        # 特征文件输入框文本改变事件
        self.featurePathEdit.textChanged.connect(self.featurePathFocusOutEvent)

    # 切换到第一个控件页面
    def display1(self):
        self.stackedWidget.setCurrentIndex(0)

    # 切换到第二个控件页面
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
        # 解析传入图片特征并匹配
        self.imgSearchClass.imgPathEdit = self.imgPathEdit.toPlainText()
        # 开启图片搜索线程
        self.imgSearchClass.start()

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
        config.read(configFile, encoding='utf-8')
        try:
            config.add_section("SETTINGS")
        except configparser.DuplicateSectionError:
            pass

        config.set("SETTINGS", "galleryPath", self.galleryPathEdit.toPlainText())
        global galleryPath
        galleryPath = self.galleryPathEdit.toPlainText()
        self.extractFeature.galleryPath = self.galleryPathEdit.toPlainText()

        with open(configFile, "w", encoding='utf-8') as config_file:
            config.write(config_file)

    # 特征文件输入文本框改变事件
    def featurePathFocusOutEvent(self):
        # print(self.featurePathEdit.toPlainText())
        config.read(configFile, encoding='utf-8')
        try:
            config.add_section("SETTINGS")
        except configparser.DuplicateSectionError:
            pass

        config.set("SETTINGS", "featurePath", self.featurePathEdit.toPlainText())
        global featurePath
        featurePath = self.featurePathEdit.toPlainText()
        self.extractFeature.featurePath = self.featurePathEdit.toPlainText()

        with open(configFile, "w", encoding='utf-8') as config_file:
            config.write(config_file)

    # 提取特征进度条进度
    def progressBarEvent(self, num):
        self.progressBar.setValue(num)
        if num == 100:
            QMessageBox.information(self, '提示', '特征提取完成', QMessageBox.Yes)
            self.progressBar.setValue(0)

    # 图片搜索完成事件
    def searchCompleteEvent(self, img_path_list):
        self.imageListWidgetUI.load_images(img_path_list)
        self.imageListWidgetUI.widget_2.setHidden(False)
        self.loadingMsgLabel.setHidden(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pages_window = MainWindow()
    pages_window.show()
    # 关闭程序，释放资源
    sys.exit(app.exec_())

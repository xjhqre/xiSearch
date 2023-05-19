# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTextEdit

import myTextEdit
from ImageListWidgetUI import ImageListWidgetUI


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 850)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(200, 0, 1000, 850))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setObjectName("frame_2")

        # 分页器
        self.stacked_widget = QtWidgets.QStackedWidget(self.frame_2)
        self.stacked_widget.setGeometry(QtCore.QRect(0, 0, 1000, 850))
        self.stacked_widget.setObjectName("stackedWidget")

        # 搜索页面
        self.search_page_widget = QtWidgets.QWidget()
        self.search_page_widget.setObjectName("searchPageWidget")
        # 搜索图片路径标签
        self.img_path_label = QtWidgets.QLabel(self.search_page_widget)
        self.img_path_label.setGeometry(QtCore.QRect(10, 30, 190, 40))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.img_path_label.setFont(font)
        self.img_path_label.setObjectName("imgPathLabel")
        # 搜索图片路径输入框
        self.img_path_edit = myTextEdit.MyTextEdit(self.search_page_widget)
        self.img_path_edit.setGeometry(QtCore.QRect(230, 30, 600, 40))
        self.img_path_edit.setObjectName("imgPathEdit")
        # 搜索按钮
        self.search_button = QtWidgets.QPushButton(self.search_page_widget)
        self.search_button.setGeometry(QtCore.QRect(870, 30, 80, 40))
        # font = QtGui.QFont()
        # font.setFamily("Arial")
        # font.setPointSize(12)
        # self.search_button.setFont(font)
        self.search_button.setObjectName("searchButton")
        # 图片流动布局
        self.vertical_layout_widget = QtWidgets.QWidget(self.search_page_widget)
        self.vertical_layout_widget.setGeometry(QtCore.QRect(10, 90, 950, 700))
        self.vertical_layout_widget.setObjectName("verticalLayoutWidget")
        self.vertical_layout = QtWidgets.QVBoxLayout(self.vertical_layout_widget)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setObjectName("verticalLayout")
        self.image_list_widget_ui = ImageListWidgetUI()
        self.image_list_widget_ui.setGeometry(QtCore.QRect(10, 90, 950, 700))
        self.vertical_layout.addWidget(self.image_list_widget_ui)
        # 搜索图片消息提示：正在搜索图片，请稍后
        self.loading_msg_label = QtWidgets.QLabel(self.vertical_layout_widget)
        self.loading_msg_label.setGeometry(QtCore.QRect(260, 300, 420, 40))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        self.loading_msg_label.setFont(font)
        self.loading_msg_label.setObjectName("loadingMsgLabel")
        self.loading_msg_label.setHidden(True)

        self.stacked_widget.addWidget(self.search_page_widget)

        # 提取特征页面
        self.excute_page_widget = QtWidgets.QWidget()
        self.excute_page_widget.setObjectName("excutePageWidget")
        # 图片库路径标签，图片库地址：
        self.gallery_path_label = QtWidgets.QLabel(self.excute_page_widget)
        self.gallery_path_label.setGeometry(QtCore.QRect(30, 30, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.gallery_path_label.setFont(font)
        self.gallery_path_label.setObjectName("galleryPathLabel")
        # 图片库路径输入框
        self.gallery_path_edit = myTextEdit.MyTextEdit(self.excute_page_widget)
        self.gallery_path_edit.setGeometry(QtCore.QRect(240, 30, 600, 40))
        self.gallery_path_edit.setObjectName("galleryPathEdit")
        # 提取特征按钮
        self.excute_button = QtWidgets.QPushButton(self.excute_page_widget)
        self.excute_button.setGeometry(QtCore.QRect(430, 120, 100, 40))
        self.excute_button.setObjectName("excuteButton")

        # 提取日志文本框
        self.extract_message = myTextEdit.MyTextEdit(self.excute_page_widget)
        self.extract_message.setReadOnly(True)
        self.extract_message.setGeometry(QtCore.QRect(130, 200, 750, 550))

        self.stacked_widget.addWidget(self.excute_page_widget)

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setEnabled(True)
        self.frame.setGeometry(QtCore.QRect(0, 0, 200, 850))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setObjectName("frame")

        # 切换图片搜索页面按钮
        self.img_search_page_button = QtWidgets.QPushButton(self.frame)
        self.img_search_page_button.setGeometry(QtCore.QRect(50, 50, 90, 40))
        self.img_search_page_button.setObjectName("imgsearchPageButton")
        # 切换提取特征页面按钮
        self.excute_page_button = QtWidgets.QPushButton(self.frame)
        self.excute_page_button.setGeometry(QtCore.QRect(50, 120, 90, 40))
        self.excute_page_button.setObjectName("excutePageButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1245, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "以图搜图   作者：xjhqre"))
        self.img_path_label.setText(_translate("MainWindow", "图片路径(可拖放)："))
        self.search_button.setText(_translate("MainWindow", "搜索"))
        self.gallery_path_label.setText(_translate("MainWindow", "图片库地址："))
        self.excute_button.setText(_translate("MainWindow", "提取特征"))
        self.img_search_page_button.setText(_translate("MainWindow", "图片搜索"))
        self.excute_page_button.setText(_translate("MainWindow", "特征抽取"))

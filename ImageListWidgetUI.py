# -*- coding: utf-8 -*-
import sys
from functools import partial

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImageReader
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from flowLayOut import FlowLayout
from myLabel import MyQLabel

'''
在使用QWiget和Qlayout时，我们可以按照以下方式嵌套：QWidget<-QLayout<-QWidget<-QLayout<-…;即QWidget中嵌入QLayout,QLayout中嵌入QWidget;
QWidget的parent只能是QWidget;
QLayout的parent可以是QWidget或者QLayout;
'''


class ImageListWidgetUI(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.resize(950, 700)
        self.imageHeight = 150 # 图片高度设置
        self.flow_layout = FlowLayout(self)
        self.widget = QWidget()
        self.widget_2 = QWidget()
        self.widget_2.setLayout(self.flow_layout)
        self.qScrollArea = QtWidgets.QScrollArea(self)
        self.qScrollArea.setGeometry(QRect(0, 0, 950, 700))
        self.qScrollArea.setWidgetResizable(True)
        self.qScrollArea.setWidget(self.widget_2)
        self.setWindowTitle("Flow Layout")

    def load_images(self, paths):
        # 清空之前的查询结果
        widget_list = list(range(self.flow_layout.count()))
        widget_list.reverse()  # 倒序删除，避免影响布局顺序

        for i in widget_list:
            item = self.flow_layout.itemAt(i)
            self.flow_layout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

        for img_path in paths:
            image_reader = QImageReader()
            image_reader.setFileName(img_path)
            image_size = image_reader.size()
            autoWidth = image_size.width() * self.imageHeight / image_size.height()
            autoWidth = int(autoWidth)
            image_size.scale(QSize(self.imageHeight, autoWidth), Qt.IgnoreAspectRatio)
            image_reader.setScaledSize(image_size)
            pixmap = image_reader.read()
            if pixmap.isNull():
                continue
            imgLabel = MyQLabel()
            imgLabel.setPixmap(QPixmap(pixmap))
            imgLabel.setScaledContents(True)
            imgLabel.setFixedHeight(self.imageHeight)
            imgLabel.setFixedWidth(autoWidth)
            imgLabel.setToolTip("点击即可复制路径")  # 气泡提示
            imgLabel.connect_customized_slot(partial(label_click_event, img_path))
            nameLabel = MyQLabel()
            nameLabel.setText(img_path)
            nameLabel.setWordWrap(True)
            # 图片和名称垂直布局
            vboxLayOut = QVBoxLayout()
            vboxLayOut.addWidget(imgLabel)
            vboxLayOut.addWidget(nameLabel)
            self.widget = QWidget()
            self.widget.setLayout(vboxLayOut)
            self.flow_layout.addWidget(self.widget)

            # 刷新界面
            QApplication.processEvents()


# 图片标签插槽函数
def label_click_event(img_path):
    clipboard = QApplication.clipboard()
    clipboard.setText(img_path)


if __name__ == '__main__':
    app = QApplication([])
    main_window = ImageListWidgetUI()
    main_window.show()
    # 数据扩充
    # image_list = image_list + image_list + image_list + image_list
    # main_window.load_images(image_list)

    # 关闭程序，释放资源
    sys.exit(app.exec_())

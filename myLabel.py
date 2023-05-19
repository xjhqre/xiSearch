from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel


class MyQLabel(QLabel):
    """
    实现点击复制标签路径信息
    """

    # 自定义信号, 注意信号必须为类属性
    button_clicked_signal = QtCore.pyqtSignal()

    def __init__(self, param=None):
        super(MyQLabel, self).__init__(param)

    def mousePressEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()

    # 可在外部与槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)


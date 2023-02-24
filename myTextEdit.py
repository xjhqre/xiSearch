from PyQt5 import QtWidgets


class MyTextEdit(QtWidgets.QTextEdit):

    def __init__(self, parent=None):
        super(MyTextEdit, self).__init__(parent)
        self.setAcceptDrops(True)  # 方法可以让该控件接收放下(Drop)事件；

    def dropEvent(self, QDropEvent):  # 6
        # Windows
        txt_path = QDropEvent.mimeData().text().replace('file:///', '')
        self.setText(txt_path)

from PyQt5 import QtWidgets


class MyTextEdit(QtWidgets.QTextEdit):

    def __init__(self, parent=None):
        super(MyTextEdit, self).__init__(parent)
        self.setAcceptDrops(True)  # 方法可以让该控件接收放下(Drop)事件；
        self.verticalScrollBar().valueChanged.connect(self.scrollbar_changed)
        self.hold_on_button = True

    # 拖入文件时去除 file:/// 前缀
    def dropEvent(self, QDropEvent):  # 6
        # Windows
        txt_path = QDropEvent.mimeData().text().replace('file:///', '')
        self.setText(txt_path)

    # 打印日志时保持滚动条在最底下
    def insertPlainText(self, text: str) -> None:
        super().insertPlainText(text)
        if self.hold_on_button:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    # 滚动条滚动事件
    def scrollbar_changed(self, value):
        if self.verticalScrollBar().maximum() == value:
            self.hold_on_button = True
        else:
            self.hold_on_button = False

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox

import config
import extract_feature_thread
import mainUI
from image_search_thread import ImageSearchThread


class MainWindow(mainUI.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        # 图片搜索线程
        self.image_search_thread = ImageSearchThread()
        self.image_search_thread.complete_signal.connect(self.search_complete_event)
        # 提取图片特征线程
        self.extract_feature_thread = extract_feature_thread.ExtractFeatureThread()
        self.extract_feature_thread.complete_signal.connect(self.extract_complete_event)
        self.extract_feature_thread.output_written.connect(self.extract_message.insertPlainText)
        # 图片库路径输入框
        self.gallery_path_edit.setText(config.gallery_path)
        # 切换到图片搜索页面按钮
        self.img_search_page_button.clicked.connect(lambda: self.display(0))
        # 切换到特征提取页面按钮
        self.excute_page_button.clicked.connect(lambda: self.display(1))
        # 搜索按钮点击事件
        self.search_button.clicked.connect(self.search_img_event)
        # 提取特征按钮点击事件
        self.excute_button.clicked.connect(self.extract_feature_event)
        # 图片库输入框改变事件
        self.gallery_path_edit.textChanged.connect(self.gallery_path_focus_out_event)
        # 搜索图片输入框改变事件
        self.img_path_edit.textChanged.connect(self.img_path_focus_out_event)

        self.show()

    def display(self, index):
        self.stacked_widget.setCurrentIndex(index)

    # 点击搜索图片按钮事件
    def search_img_event(self):
        if config.search_img_path == "":
            QMessageBox.information(self, '提示', '请设置查询图片', QMessageBox.Yes)
            return
        self.loading_msg_label.setText("正在搜索图片，请稍后")
        self.loading_msg_label.setHidden(False)
        self.image_list_widget_ui.widget.setHidden(True)
        # 开启图片搜索线程
        self.image_search_thread.start()

    # 提取图片库特征事件
    def extract_feature_event(self):
        if config.gallery_path == "":
            QMessageBox.information(self, '提示', '请设置图片库路径', QMessageBox.Yes)
            return
        # 清空日志文本框
        self.extract_message.clear()
        self.extract_feature_thread.start()

    # 图片库输入文本框改变事件
    def gallery_path_focus_out_event(self):
        config.gallery_path = self.gallery_path_edit.toPlainText()
        config.update_gallery_path(self.gallery_path_edit.toPlainText())

    # 搜索图片文本框改变事件
    def img_path_focus_out_event(self):
        config.search_img_path = self.img_path_edit.toPlainText()

    # 图片搜索完成事件
    def search_complete_event(self, img_path_list):
        self.image_list_widget_ui.load_images(img_path_list)
        self.image_list_widget_ui.widget.setHidden(False)
        self.loading_msg_label.setHidden(True)

    # 特征提取完成事件
    def extract_complete_event(self):
        QMessageBox.information(self, '提示', '特征提取完成', QMessageBox.Yes)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pages_window = MainWindow()
    pages_window.show()
    # 关闭程序，释放资源
    sys.exit(app.exec_())

from PyQt5.QtCore import QThread, pyqtSignal

import config
import sentence_transformer_utils


class ImageSearchThread(QThread):
    """
    图片搜索线程
    """

    complete_signal = pyqtSignal(list)  # 搜素完成信号

    def __init__(self):
        super(ImageSearchThread, self).__init__()

    def run(self):
        self.complete_signal.emit(sentence_transformer_utils.search(config.search_img_path))

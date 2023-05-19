import sys
import traceback

from PyQt5.QtCore import QThread, pyqtSignal

import sentence_transformer_utils


class ExtractFeatureThread(QThread):
    complete_signal = pyqtSignal()  # 提取图片特征完成信号
    output_written = pyqtSignal(str)

    def __init__(self):
        super(ExtractFeatureThread, self).__init__()
        sys.stdout = self
        sys.stderr = self

    def write(self, text):
        self.output_written.emit(str(text))

    def run(self):
        try:
            sentence_transformer_utils.extract()
        except Exception as e:
            traceback.print_exc()
            print()
        else:
            self.complete_signal.emit()

"""
没有特征文件异常
"""


class NoFeatureFileException(Exception):
    def __init__(self):
        super().__init__()

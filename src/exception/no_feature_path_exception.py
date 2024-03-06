"""
没有设置特征文件保存路径异常
"""


class NoFeaturePathException(Exception):
    def __init__(self):
        super().__init__()

class Log:
    """
    日志
    """

    def __init__(self):
        self._cnt = 0  # 提取图片计数
        self._time = 0  # 提取图片耗时
        self._error_img_path = []  # 提取失败图片路径集合
        self._finish = 0  # 是否完成

    @property
    def cnt(self):
        return self._cnt

    @cnt.setter
    def cnt(self, value):
        self._cnt = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def error_img_path(self):
        return self._error_img_path

    @error_img_path.setter
    def error_img_path(self, value):
        self._error_img_path = value

    @property
    def finish(self):
        return self._finish

    @finish.setter
    def finish(self, value):
        self._finish = value


log = Log()

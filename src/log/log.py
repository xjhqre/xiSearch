class Log:
    """
    日志
    """

    def __init__(self):
        self._extract_log: str = ""  # 提取日志

    @property
    def extract_log(self):
        return self._extract_log

    @extract_log.setter
    def extract_log(self, value):
        self._extract_log = value


log = Log()

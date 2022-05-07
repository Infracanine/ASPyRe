from datetime import datetime
from enum import Enum


# TODO: Implement this to provide multiple levels of logging
class LogLevels(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2


class MyLogger():
    def log(self, message: str):
        now = datetime.now()
        print(f"{now.strftime('%d-%m-%Y-%H:%M:%S')}|PyViz|{message} ")


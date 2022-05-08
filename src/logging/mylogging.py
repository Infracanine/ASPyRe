from datetime import datetime
from enum import Enum


# TODO: Implement this to provide multiple levels of logging
class LogLevels(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2


class MyLogger:
    def log(self, message: str, log_loc = "PyViz"):
        now = datetime.now()
        print(f"{now.strftime('%d-%m-%Y-%H:%M:%S')}|{log_loc}|{message} ")


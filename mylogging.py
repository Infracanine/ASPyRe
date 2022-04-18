from datetime import datetime
from enum import Enum

class LogLevels(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2


def log(message: str):
    now = datetime.now()
    print(f"{now.strftime('%d-%m-%Y-%H:%M:%S')}|{message} ")


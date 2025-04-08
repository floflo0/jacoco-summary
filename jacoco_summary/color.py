from enum import Enum


class Color(Enum):
    RESET = '\x1b[0m'
    GRAY  = '\x1b[30m'
    RED   = '\x1b[31m'
    GREEN = '\x1b[32m'

    def __str__(self) -> str:
        return self.value

from enum import Enum


class CounterType(Enum):
    BRANCH      = 'BRANCH'
    CLASS       = 'CLASS'
    COMPLEXITY  = 'COMPLEXITY'
    INSTRUCTION = 'INSTRUCTION'
    LINE        = 'LINE'
    METHOD      = 'METHOD'

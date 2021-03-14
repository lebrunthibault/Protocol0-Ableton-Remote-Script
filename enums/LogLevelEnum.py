from a_protocol_0.enums.AbstractEnum import AbstractEnum


class LogLevelEnum(AbstractEnum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    EXCLUSIVE_LOG = 5


ACTIVE_LOG_LEVEL = LogLevelEnum.DEBUG

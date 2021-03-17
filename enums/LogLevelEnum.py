from a_protocol_0.enums.AbstractEnum import AbstractEnum


class LogLevelEnum(AbstractEnum):
    DEV = 1
    DEBUG = 2
    INFO = 3
    NOTICE = 4
    WARNING = 5
    ERROR = 6
    EXCLUSIVE_LOG = 7


ACTIVE_LOG_LEVEL = LogLevelEnum.DEBUG

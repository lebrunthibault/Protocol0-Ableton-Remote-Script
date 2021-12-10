from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.enums.LogLevelEnum import LogLevelEnum


class Config(object):
    LOG_LEVEL = LogLevelEnum.DEV
    SHOW_RELOAD_TIME = True
    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = False

    ABLETON_SESSION_TYPE = AbletonSessionTypeEnum.NORMAL

    SPLIT_QUANTIZATION_TEMPO = 110

    SET_EXCEPTHOOK = False
    VOLUME_LISTENER_ACTIVE = False

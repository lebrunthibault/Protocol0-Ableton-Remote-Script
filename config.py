from protocol0.enums.LogLevelEnum import LogLevelEnum


class Config(object):
    LOG_LEVEL = LogLevelEnum.DEV
    SHOW_RELOAD_TIME = True
    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = False

    SPLIT_QUANTIZATION_TEMPO = 110

    SET_EXCEPTHOOK = False
    VOLUME_LISTENER_ACTIVE = False

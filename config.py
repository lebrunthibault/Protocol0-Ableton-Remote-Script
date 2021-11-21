from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.enums.LogLevelEnum import LogLevelEnum


class Config(object):
    LOG_LEVEL = LogLevelEnum.DEV
    ABLETON_SESSION_TYPE = AbletonSessionTypeEnum.NORMAL
    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = False

    SPLIT_QUANTIZATION_TEMPO = 110

    SET_EXCEPTHOOK = False
    MIX_VOLUME_FOLLOWER = False

    DISABLE_CRASHING_METHODS = True
    INSTRUMENT_BUS_TRACK_NAME = "Instrument bus"

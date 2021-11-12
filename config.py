from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum


class Config(object):
    ABLETON_SESSION_TYPE = AbletonSessionTypeEnum.NORMAL
    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = False

    SET_EXCEPTHOOK = True
    MIX_VOLUME_FOLLOWER = False

    DISABLE_CRASHING_METHODS = True

from typing import Optional

from protocol0.domain.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.domain.enums.LogLevelEnum import LogLevelEnum
from protocol0.domain.enums.RecordTypeEnum import RecordTypeEnum


class Config(object):
    LOG_LEVEL = LogLevelEnum.DEV
    SHOW_RELOAD_TIME = True
    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = False

    ABLETON_SESSION_TYPE = AbletonSessionTypeEnum.NORMAL
    CURRENT_RECORD_TYPE = None  # type: Optional[RecordTypeEnum]

    SPLIT_QUANTIZATION_TEMPO = 110

    ZERO_DB_VOLUME = 0.850000023842
    CLIPPING_TRACK_VOLUME = 0.91

    SET_EXCEPTHOOK = False
    VOLUME_LISTENER_ACTIVE = False

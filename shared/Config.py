from os.path import dirname, realpath

from typing import Optional

from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.LogLevelEnum import LogLevelEnum


class Config(object):
    PROJECT_ROOT = dirname(dirname(realpath(__file__)))
    REMOTE_SCRIPTS_ROOT = dirname(PROJECT_ROOT)
    LOG_LEVEL = LogLevelEnum.DEV
    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = False

    FOCUS_PROPHET_ON_STARTUP = False
    CURRENT_RECORD_TYPE = None  # type: Optional[RecordTypeEnum]

    SPLIT_QUANTIZATION_TEMPO = 110

    ZERO_DB_VOLUME = 0.850000023842
    CLIPPING_TRACK_VOLUME = 0.91

    VOLUME_LISTENER_ACTIVE = False

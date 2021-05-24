import os

from a_protocol_0.enums.LogLevelEnum import LogLevelEnum


class Config(object):
    LOG_LEVEL = LogLevelEnum.DEV

    # with this set to True, the script is going to rename more aggressively
    FIX_OUTDATED_SETS = str(os.getenv("FIX_OUTDATED_SETS")).lower() == "true"  # type: bool

    SEQUENCE_DEBUG_MODE = str(os.getenv("DEBUG_SEQUENCE")).lower() == "true"
    SEQUENCE_SILENT_MODE = str(os.getenv("DEBUG_SEQUENCE")).lower() != "true"

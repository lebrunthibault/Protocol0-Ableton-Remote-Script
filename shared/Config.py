import os
from os.path import dirname, realpath

from protocol0.shared.logging.LogLevelEnum import LogLevelEnum


class Config(object):
    PROJECT_ROOT = dirname(dirname(realpath(__file__)))
    REMOTE_SCRIPTS_ROOT = dirname(PROJECT_ROOT)

    SAMPLE_PATH = str(os.getenv("SAMPLE_PATH"))

    LOG_LEVEL = LogLevelEnum.DEV

    FOCUS_PROPHET_ON_STARTUP = False

    SPLIT_QUANTIZATION_TEMPO = 110

    ZERO_DB_VOLUME = 0.850000023842
    CLIPPING_TRACK_VOLUME = 0.91

import os
from os.path import dirname, realpath

from protocol0.shared.logging.LogLevelEnum import LogLevelEnum


class Config(object):
    # DIRECTORIES
    PROJECT_ROOT = dirname(dirname(realpath(__file__)))
    REMOTE_SCRIPTS_ROOT = dirname(PROJECT_ROOT)
    SAMPLE_DIRECTORY = str(os.getenv("SAMPLE_DIRECTORY"))

    # SERVICES
    SENTRY_DSN = os.getenv("SENTRY_DSN")

    # MISC
    EXPERIMENTAL_FEATURES = False

    LOG_LEVEL = LogLevelEnum.DEV

    SPLIT_QUANTIZATION_TEMPO = 110

    TRACK_VOLUME_MONITORING = False

    # VOLUME CONSTANTS
    ZERO_VOLUME = 0.850000023842
    ZERO_VOLUME_DB = -pow(10, 6)
    CLIPPING_TRACK_VOLUME = 0.91

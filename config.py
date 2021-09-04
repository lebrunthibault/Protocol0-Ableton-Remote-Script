import os
import os
from fractions import Fraction
from os.path import dirname

import Live
from protocol0.enums.LogLevelEnum import LogLevelEnum


class Config(object):
    LOG_LEVEL = LogLevelEnum.DEV

    # with this set to True, the script is going to rename more aggressively
    FIX_OUTDATED_SETS = True

    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = True


PROJECT_ROOT = dirname(os.path.realpath(__file__))
REMOTE_SCRIPTS_ROOT = dirname(PROJECT_ROOT)

QUANTIZATION_OPTIONS = [
    Live.Song.RecordingQuantization.rec_q_no_q,
    Live.Song.RecordingQuantization.rec_q_quarter,
    Live.Song.RecordingQuantization.rec_q_eight,
    Live.Song.RecordingQuantization.rec_q_eight_triplet,
    Live.Song.RecordingQuantization.rec_q_eight_eight_triplet,
    Live.Song.RecordingQuantization.rec_q_sixtenth,
    Live.Song.RecordingQuantization.rec_q_sixtenth_triplet,
    Live.Song.RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
    Live.Song.RecordingQuantization.rec_q_thirtysecond,
]
PUSH2_BEAT_QUANTIZATION_STEPS = [
    Fraction(1, 48),
    Fraction(1, 32),
    Fraction(1, 24),
    Fraction(1, 16),
    Fraction(1, 12),
    Fraction(1, 8),
    Fraction(1, 6),
    Fraction(1, 4),
]

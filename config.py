import os
from fractions import Fraction
from os.path import dirname

import Live


class Config(object):
    SEQUENCE_DEBUG = False
    SEQUENCE_SLOW_MO = False

    SET_EXCEPTHOOK = True
    MIX_VOLUME_FOLLOWER = False


PROJECT_ROOT = dirname(os.path.realpath(__file__))
REMOTE_SCRIPTS_ROOT = dirname(PROJECT_ROOT)

BAR_LENGTHS = [1, 2, 4, 8, 16, 32, 64]

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

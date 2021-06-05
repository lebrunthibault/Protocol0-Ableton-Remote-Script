import os
from fractions import Fraction
from os.path import dirname

import Live

ROOT_DIR = dirname(os.path.realpath(__file__))
ABLETON_EXE = "Ableton Live 10 Suite.exe"
SERVER_DIR = str(os.getenv("SERVER_PATH"))
REMOTE_SCRIPTS_DIR = dirname(ROOT_DIR)

MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}
RecordingQuantization = Live.Song.RecordingQuantization
QUANTIZATION_OPTIONS = [
    RecordingQuantization.rec_q_no_q,
    RecordingQuantization.rec_q_quarter,
    RecordingQuantization.rec_q_eight,
    RecordingQuantization.rec_q_eight_triplet,
    RecordingQuantization.rec_q_eight_eight_triplet,
    RecordingQuantization.rec_q_sixtenth,
    RecordingQuantization.rec_q_sixtenth_triplet,
    RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
    RecordingQuantization.rec_q_thirtysecond,
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

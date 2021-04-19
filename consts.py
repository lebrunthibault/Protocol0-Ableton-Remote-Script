import os
from fractions import Fraction
from os.path import dirname

ROOT_DIR = dirname(os.path.realpath(__file__))
REMOTE_SCRIPTS_DIR = dirname(ROOT_DIR)

MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}
RECORDING_TIMES = ["1 bar", "2 bars", "4 bars", "8 bars", "16 bars", "32 bars", "64 bars"]
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

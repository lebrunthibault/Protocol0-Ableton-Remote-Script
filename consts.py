import os
from fractions import Fraction
from os.path import dirname

MIDI_STATUS_BYTES = {'note': 144, 'cc': 176, 'pc': 192}
RECORDING_TIMES = ["1 bar", "2 bars", "4 bars", "8 bars", "16 bars", "32 bars"]
TRACK_CATEGORY_DRUMS = "Drums"
TRACK_CATEGORY_OTHER = "Other"
TRACK_CATEGORY_ALL = "All"
TRACK_CATEGORIES = [TRACK_CATEGORY_DRUMS, TRACK_CATEGORY_OTHER, TRACK_CATEGORY_ALL]

RESTART_SOLO_STOPPED = "Solo stopped"
RESET_SOLO_PLAY = "Reset solo play"
PLAY_MENU_OPTIONS = [RESTART_SOLO_STOPPED, RESET_SOLO_PLAY]

ABLETON_USER_LIBRARY_PATH = "C:\\Users\\thiba\\Google Drive\\music\\software presets\\Ableton User Library"
PROTOCOL0_FOLDER = dirname(os.path.realpath(__file__))
REMOTE_SCRIPTS_FOLDER = dirname(PROTOCOL0_FOLDER)
SAMPLE_PATH = ABLETON_USER_LIBRARY_PATH + "\\Samples\\Imported"
EXTERNAL_SYNTH_PROPHET_NAME = "prophet"
EXTERNAL_SYNTH_MINITAUR_NAME = "minitaur"
AUTOMATION_TRACK_MIDI_NAME = "automation midi"
AUTOMATION_TRACK_AUDIO_NAME = "automation audio"
EXTERNAL_SYNTH_NAMES = (EXTERNAL_SYNTH_PROPHET_NAME, EXTERNAL_SYNTH_MINITAUR_NAME)

INSTRUMENT_NAME_MAPPINGS = {
    "Serum_x64": "InstrumentSerum",
    "Minitaur Editor-VI(x64)": "InstrumentMinitaur",
    "REV2Editor": "InstrumentProphet",
}

push2_beat_quantization_steps = [v * 4 for v in [
    Fraction(1, 48),
    Fraction(1, 32),
    Fraction(1, 24),
    Fraction(1, 16),
    Fraction(1, 12),
    Fraction(1, 8),
    Fraction(1, 6),
    Fraction(1, 4)]]


class LogLevel:
    ACTIVE_LOG_LEVEL = None
    DEBUG = 1
    INFO = 2
    ERROR = 3
    EXCLUSIVE_LOG = 4

    _values_dict = {}

    @staticmethod
    def value_to_name(value):
        # type: (int) -> str
        if value not in LogLevel._values_dict:
            raise RuntimeError("You gave an inexistent value for class LogLevel")
        return LogLevel._values_dict[value]


LogLevel._values_dict = {v: k for k, v in [item for item in vars(LogLevel).items() if isinstance(item[1], int)]}
LogLevel.ACTIVE_LOG_LEVEL = LogLevel.DEBUG

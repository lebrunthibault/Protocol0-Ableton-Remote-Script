from os.path import dirname

MIDI_STATUS_BYTES = {'note': 144, 'cc': 176, 'pc': 192}
RECORDING_TIMES = ["1 bar", "2 bars", "4 bars", "8 bars", "16 bars", "32 bars"]
TRACK_CATEGORY_DRUMS = "Drums"
TRACK_CATEGORY_OTHER = "Other"
TRACK_CATEGORY_ALL = "All"
TRACK_CATEGORIES = [TRACK_CATEGORY_DRUMS, TRACK_CATEGORY_OTHER, TRACK_CATEGORY_ALL]
ABLETON_USER_LIBRARY_PATH = "C:\\Users\\thiba\\Google Drive\\music\\software presets\\Ableton User Library"
PROTOCOL0_FOLDER = dirname(__file__)
REMOTE_SCRIPTS_FOLDER = dirname(PROTOCOL0_FOLDER)
SAMPLE_PATH = ABLETON_USER_LIBRARY_PATH + "\\Samples\\Imported"
EXTERNAL_SYNTH_PROPHET_NAME = "Prophet"
EXTERNAL_SYNTH_MINITAUR_NAME = "Minitaur"
EXTERNAL_SYNTH_NAMES = (EXTERNAL_SYNTH_PROPHET_NAME, EXTERNAL_SYNTH_MINITAUR_NAME)

INSTRUMENT_NAME_MAPPINGS = {
    "Serum_x64": "InstrumentSerum",
    "Minitaur Editor-VI(x64)": "InstrumentMinitaur",
    "REV2Editor": "InstrumentProphet",
}


class LogLevel:
    DEBUG = 1
    INFO = 2


ACTIVE_LOG_LEVEL = LogLevel.DEBUG

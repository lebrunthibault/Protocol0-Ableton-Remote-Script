from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.enums.ColorEnum import ColorEnum


class InstrumentMinitaur(AbstractExternalSynthTrackInstrument):
    MONOPHONIC = True
    NAME = "Minitaur"
    DEVICE_NAME = "minitaur editor(x64)"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = ColorEnum.MINITAUR
    CAN_BE_SHOWN = False
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    PROGRAM_CHANGE_OFFSET = 1
    RECORD_CLIP_TAILS = False
    HAS_PROTECTED_MODE = False

    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 1.4

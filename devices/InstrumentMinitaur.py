from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.ColorEnum import ColorEnum


class InstrumentMinitaur(AbstractInstrument):
    NAME = "Minitaur Bass"
    DEVICE_NAME = "minitaur editor(x64)"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = ColorEnum.MINITAUR
    CAN_BE_SHOWN = True
    IS_EXTERNAL_SYNTH = True
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    PROGRAM_CHANGE_OFFSET = 1
    HAS_TOTAL_RECALL = False

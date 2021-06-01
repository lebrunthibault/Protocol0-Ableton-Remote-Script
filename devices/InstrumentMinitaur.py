from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.ColorEnum import ColorEnum


class InstrumentMinitaur(AbstractInstrument):
    NAME = "Minitaur"
    DEVICE_NAME = "minitaur editor(x64)"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = ColorEnum.MINITAUR
    CAN_BE_SHOWN = True
    IS_EXTERNAL_SYNTH = True
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    PROGRAM_CHANGE_OFFSET = 1

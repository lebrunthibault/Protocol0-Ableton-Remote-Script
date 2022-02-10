from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentMinitaur(InstrumentInterface):
    NAME = "Minitaur"
    DEVICE_NAME = "minitaur editor(x64)"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = InstrumentColorEnum.MINITAUR
    CAN_BE_SHOWN = False
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    PROGRAM_CHANGE_OFFSET = 1
    HAS_PROTECTED_MODE = False
    MONOPHONIC = True

    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 1.4

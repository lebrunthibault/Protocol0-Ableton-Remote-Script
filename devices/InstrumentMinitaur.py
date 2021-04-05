from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.Colors import Colors


class InstrumentMinitaur(AbstractInstrument):
    NAME = "minitaur"
    TRACK_COLOR = Colors.MINITAUR
    IS_EXTERNAL_SYNTH = True
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    PROGRAM_CHANGE_OFFSET = 1


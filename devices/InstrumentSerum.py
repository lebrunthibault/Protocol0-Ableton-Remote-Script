from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.Colors import Colors


class InstrumentSerum(AbstractInstrument):
    NAME = "Serum"
    TRACK_COLOR = Colors.SERUM
    PRESETS_PATH = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"
    NEEDS_ACTIVATION_FOR_PRESETS_CHANGE = True

    def format_preset_name(self, preset_name):
        # type: (str) -> str
        return preset_name.replace("User\\", "")

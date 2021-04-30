from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.ColorEnum import ColorEnum


class InstrumentSerum(AbstractInstrument):  # noqa
    NAME = "Serum"
    DEVICE_NAME = "serum_x64"
    TRACK_COLOR = ColorEnum.SERUM
    PRESETS_PATH = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"
    NEEDS_ACTIVATION_FOR_PRESETS_CHANGE = True

    def format_preset_name(self, preset_name):
        # type: (str) -> str
        return preset_name.replace("User\\", "")

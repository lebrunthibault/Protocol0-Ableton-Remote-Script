from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentSerum(InstrumentInterface):
    NAME = "Serum"
    DEVICE_NAME = "serum_x64"
    TRACK_COLOR = ColorEnum.SERUM
    PRESETS_PATH = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"

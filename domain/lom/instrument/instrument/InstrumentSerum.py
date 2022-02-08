from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentSerum(InstrumentInterface):
    NAME = "Serum"
    DEVICE_NAME = "serum_x64"
    TRACK_COLOR = InstrumentColorEnum.SERUM
    PRESETS_PATH = "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"

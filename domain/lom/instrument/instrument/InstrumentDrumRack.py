from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum


class InstrumentDrumRack(InstrumentInterface):
    NAME = "Drum Rack"
    TRACK_COLOR = InstrumentColorEnum.SIMPLER
    CAN_BE_SHOWN = False
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NONE
    DEFAULT_NOTE = 36

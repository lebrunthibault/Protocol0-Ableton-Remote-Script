from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum


class InstrumentDrumRack(InstrumentInterface):
    NAME = "Drum Rack"
    TRACK_COLOR = ColorEnum.SIMPLER
    CAN_BE_SHOWN = False
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NONE

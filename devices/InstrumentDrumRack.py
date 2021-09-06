from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.ColorEnum import ColorEnum


class InstrumentDrumRack(AbstractInstrument):
    NAME = "Drum Rack"
    TRACK_COLOR = ColorEnum.DRUM_RACK
    CAN_BE_SHOWN = False
    PRESET_DISPLAY_OPTION = None


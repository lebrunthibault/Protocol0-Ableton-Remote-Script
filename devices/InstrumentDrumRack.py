from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.ColorEnum import ColorEnum


class InstrumentDrumRack(AbstractInstrument):
    NAME = "Drum Rack"
    TRACK_COLOR = ColorEnum.DRUM_RACK
    CAN_BE_SHOWN = False

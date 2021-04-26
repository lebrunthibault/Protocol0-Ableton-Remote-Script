from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.Colors import Colors


class InstrumentDrumRack(AbstractInstrument):
    NAME = "Drum Rack"
    TRACK_COLOR = Colors.DRUM_RACK
    CAN_BE_SHOWN = False

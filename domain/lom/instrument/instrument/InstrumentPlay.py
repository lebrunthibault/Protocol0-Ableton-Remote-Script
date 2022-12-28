from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentPlay(InstrumentInterface):  # noqa
    NAME = "Play"
    DEVICE = DeviceEnum.PLAY
    TRACK_COLOR = InstrumentColorEnum.PLAY

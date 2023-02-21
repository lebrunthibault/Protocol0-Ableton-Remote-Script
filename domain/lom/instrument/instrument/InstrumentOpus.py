from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentOpus(InstrumentInterface):  # noqa
    NAME = "Opus"
    DEVICE = DeviceEnum.OPUS
    TRACK_COLOR = InstrumentColorEnum.OPUS

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentKontakt(InstrumentInterface):  # noqa
    NAME = "Kontakt"
    DEVICE = DeviceEnum.KONTAKT
    TRACK_COLOR = InstrumentColorEnum.KONTAKT

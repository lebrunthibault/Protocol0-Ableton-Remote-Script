from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentKontakt(InstrumentInterface):  # noqa
    NAME = "Kontakt"
    DEVICE_NAME = DeviceEnum.KONTAKT.device_name
    TRACK_COLOR = InstrumentColorEnum.ADDICTIVE_KEYS

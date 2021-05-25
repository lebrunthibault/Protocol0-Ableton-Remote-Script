from typing import Any

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.enums.ColorEnum import ColorEnum
from a_protocol_0.lom.device.RackDevice import RackDevice


class InstrumentAddictiveKeys(AbstractInstrument):  # noqa
    NAME = "Addictive Keys"
    DEVICE_NAME = "Addictive Keys"
    TRACK_COLOR = ColorEnum.ADDICTIVE_KEYS

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentAddictiveKeys, self).__init__(*a, **k)
        self.device = self.device  # type: RackDevice
        self.DEFAULT_NUMBER_OF_PRESETS = len(self.device.chains)

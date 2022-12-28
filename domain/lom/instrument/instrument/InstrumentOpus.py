from typing import Optional

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentOpus(InstrumentInterface):  # noqa
    NAME = "Opus"
    DEVICE = DeviceEnum.OPUS
    TRACK_COLOR = InstrumentColorEnum.OPUS

    def post_activate(self):
        # type: () -> Optional[Sequence]
        # show the play tab
        Backend.client().click(635, 51)

        return Sequence().wait(20).done()

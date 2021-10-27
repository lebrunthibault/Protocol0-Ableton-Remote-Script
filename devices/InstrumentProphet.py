from typing import Any, Optional

from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.enums.ColorEnum import ColorEnum
from protocol0.enums.DeviceNameEnum import DeviceNameEnum
from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.sequence.Sequence import Sequence


class InstrumentProphet(AbstractExternalSynthTrackInstrument):
    NAME = "Prophet"
    DEVICE_NAME = "rev2editor"
    TRACK_COLOR = ColorEnum.PROPHET
    EXTERNAL_INSTRUMENT_DEVICE = DeviceNameEnum.EXTERNAL_AUDIO_EFFECT
    AUDIO_INPUT_ROUTING_CHANNEL = InputRoutingChannelEnum.POST_FX
    ACTIVE_INSTANCE = None  # type: Optional[InstrumentProphet]

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentProphet, self).__init__(*a, **k)

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        return InstrumentProphet.ACTIVE_INSTANCE != self

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        InstrumentProphet.ACTIVE_INSTANCE = self
        seq = Sequence()
        seq.add(wait=5)
        seq.add(self.system.activate_rev2_editor, wait=5)
        return seq.done()

    def post_activate(self):
        # type: () -> Optional[Sequence]
        seq = Sequence()
        seq.add(self.system.post_activate_rev2_editor, wait=20)
        return seq.done()

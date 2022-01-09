from typing import Optional

from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.enums.ColorEnum import ColorEnum
from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.sequence.Sequence import Sequence


class InstrumentProphet(AbstractExternalSynthTrackInstrument):
    NAME = "Prophet"
    DEVICE_NAME = "rev2editor"
    TRACK_COLOR = ColorEnum.PROPHET
    ACTIVE_INSTANCE = None  # type: Optional[InstrumentProphet]

    MIDI_INPUT_ROUTING_TYPE = InputRoutingTypeEnum.REV2_AUX
    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 3.2

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

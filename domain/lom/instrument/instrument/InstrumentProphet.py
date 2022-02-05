from functools import partial

from typing import Optional, Any

from protocol0.domain.lom.instrument.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.infra.System import System


class InstrumentProphet(AbstractExternalSynthTrackInstrument):
    NAME = "Prophet"
    DEVICE_NAME = "rev2editor"
    TRACK_COLOR = ColorEnum.PROPHET
    ACTIVE_INSTANCE = None  # type: Optional[InstrumentProphet]

    MIDI_INPUT_ROUTING_TYPE = InputRoutingTypeEnum.REV2_AUX
    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 3.2
    EDITOR_DEVICE_ON = True

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentProphet, self).__init__(*a, **k)
        Scheduler.defer(partial(setattr, self.device, "device_on", InstrumentProphet.EDITOR_DEVICE_ON))

    @property
    def needs_exclusive_activation(self):
        # type: () -> bool
        return InstrumentProphet.ACTIVE_INSTANCE != self

    def exclusive_activate(self):
        # type: () -> Optional[Sequence]
        InstrumentProphet.ACTIVE_INSTANCE = self
        seq = Sequence()
        seq.add(wait=5)
        seq.add(System.get_instance().activate_rev2_editor, wait=5)
        return seq.done()

    def post_activate(self):
        # type: () -> Optional[Sequence]
        seq = Sequence()
        seq.add(System.get_instance().post_activate_rev2_editor, wait=20)
        return seq.done()

    @classmethod
    def toggle_editor_plugin_on(cls):
        # type: () -> None
        """
            Having big issues with codeknobs editor that doesn't always behave in the same way

            Sometimes the editor doesn't work as expected and generates duplicate midi messages (it seems).
            Notes off messages are generated instantly resulting in very short notes

            In that case, the editor will work even toggled off ..
            So we need to toggle if off but still activate it shortly at certain moments
            to have the notes AND nrpn messages work as expected.
        """
        InstrumentProphet.EDITOR_DEVICE_ON = not InstrumentProphet.EDITOR_DEVICE_ON

        from protocol0 import Protocol0
        Protocol0.SELF.show_message("Rev2 editor %s" % ("ON" if InstrumentProphet.EDITOR_DEVICE_ON else "OFF"))
        from protocol0.domain.lom.song.Song import Song

        for prophet_track in Song.get_instance().prophet_tracks:
            prophet_track.instrument.device.device_on = InstrumentProphet.EDITOR_DEVICE_ON

    def activate_editor_automation(self):
        # type: () -> Sequence
        seq = Sequence()
        if self and self.device and InstrumentProphet.EDITOR_DEVICE_ON is False:
            self.device.device_on = True
            seq.add(wait=15)
            seq.add(partial(setattr, self.device, "device_on", False))

        return seq.done()

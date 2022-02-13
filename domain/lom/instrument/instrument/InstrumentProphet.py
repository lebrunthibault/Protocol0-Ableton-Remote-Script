from functools import partial

from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.InstrumentWithEditorInterface import InstrumentWithEditorInterface
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.shared.System import System
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class InstrumentProphet(InstrumentInterface, InstrumentWithEditorInterface):
    NAME = "Prophet"
    DEVICE_NAME = "rev2editor"
    TRACK_COLOR = InstrumentColorEnum.PROPHET
    ACTIVE_INSTANCE = None  # type: Optional[InstrumentProphet]

    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 3.2
    EDITOR_DEVICE_ON = False
    MIDI_INPUT_ROUTING_TYPE = InputRoutingTypeEnum.REV2_AUX

    def __init__(self, track, device):
        # type: (SimpleTrack, Optional[Device]) -> None
        super(InstrumentProphet, self).__init__(track, device)
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
        seq.add(System.client().activate_rev2_editor, wait=5)
        return seq.done()

    def post_activate(self):
        # type: () -> Optional[Sequence]
        seq = Sequence()
        seq.add(System.client().post_activate_rev2_editor, wait=20)
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
        cls.EDITOR_DEVICE_ON = not cls.EDITOR_DEVICE_ON

        StatusBar.show_message("Rev2 editor %s" % ("ON" if cls.EDITOR_DEVICE_ON else "OFF"))

        for prophet_track in SongFacade.prophet_tracks():
            prophet_track.instrument.device.device_on = cls.EDITOR_DEVICE_ON

    def activate_editor_automation(self):
        # type: () -> Sequence
        seq = Sequence()
        if self and self.device and InstrumentProphet.EDITOR_DEVICE_ON is False:
            self.device.device_on = True
            seq.add(wait=15)
            seq.add(partial(setattr, self.device, "device_on", False))

        return seq.done()

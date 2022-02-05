from functools import partial

from typing import Optional, Any

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.DomainEventBus import DomainEventBus
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.simple_track.event.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.infra.System import System


class InstrumentDisplayManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentDisplayManager, self).__init__(*a, **k)
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self.handle_armed_simple_track)

    def show_hide_instrument(self):
        # type: () -> Optional[Sequence]
        instrument = self.song.current_track.instrument
        if not instrument or not instrument.CAN_BE_SHOWN:
            return None

        seq = Sequence()
        if instrument.needs_activation:
            seq.add(partial(self.activate_plugin_window, select_instrument_track=True))
        else:
            seq.add(instrument.device.track.select)
            if self.song.selected_track != instrument.device.track:
                seq.add(System.get_instance().show_plugins)
            else:
                seq.add(System.get_instance().show_hide_plugins)
        return seq.done()

    def activate_instrument_plugin_window(self):
        # type: () -> None
        instrument = self.song.current_track.instrument
        if instrument and instrument.CAN_BE_SHOWN:
            self.activate_plugin_window(instrument, force_activate=True)

    def handle_armed_simple_track(self, event):
        # type: (SimpleTrackArmedEvent) -> Sequence
        seq = Sequence()
        if event.track.instrument and event.track.instrument.needs_exclusive_activation:
            seq.add(partial(self.activate_plugin_window, event.track.instrument))
        return seq.done()

    def activate_plugin_window(self, instrument, select_instrument_track=False, force_activate=False):
        # type: (InstrumentInterface, bool, bool) -> Optional[Sequence]
        seq = Sequence()

        if force_activate or not instrument.activated:
            seq.add(instrument.device.track.select)
            seq.add(partial(self.parent.deviceManager.make_plugin_window_showable, instrument.device))
            seq.add(lambda: setattr(self, "activated", True), name="mark instrument as activated")

        if force_activate or instrument.needs_exclusive_activation:
            seq.add(instrument.device.track.select)
            seq.add(instrument.exclusive_activate)

        if force_activate or not instrument.activated:
            seq.add(instrument.post_activate)

        if not force_activate and not select_instrument_track:
            seq.add(wait=2)
            seq.add(System.get_instance().hide_plugins)

        return seq.done()
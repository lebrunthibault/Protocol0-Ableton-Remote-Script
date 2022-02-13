from functools import partial

from typing import Optional

from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.simple_track.event.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.System import System
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentDisplayService(object):
    def __init__(self, device_service):
        # type: (DeviceService) -> None
        self._device_service = device_service
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._handle_simple_track_armed_event)

    def show_hide_instrument(self, instrument):
        # type: (InstrumentInterface) -> Optional[Sequence]
        if not instrument.CAN_BE_SHOWN:
            return None

        seq = Sequence()
        if not instrument.activated or instrument.needs_exclusive_activation:
            seq.add(partial(self.activate_plugin_window, instrument, select_instrument_track=True))
        else:
            seq.add(instrument.device.track.select)
            if SongFacade.selected_track() != instrument.device.track:
                seq.add(System.client().show_plugins)
            else:
                seq.add(System.client().show_hide_plugins)
        return seq.done()

    def activate_instrument_plugin_window(self, instrument):
        # type: (InstrumentInterface) -> None
        if instrument.CAN_BE_SHOWN:
            self.activate_plugin_window(instrument, force_activate=True)

    def _handle_simple_track_armed_event(self, event):
        # type: (SimpleTrackArmedEvent) -> Sequence
        seq = Sequence()
        if event.track.instrument and event.track.instrument.needs_exclusive_activation:
            seq.add(partial(self.activate_plugin_window, event.track.instrument))
            seq.add(wait=10)
            seq.add(System.client().hide_plugins)
        return seq.done()

    def activate_plugin_window(self, instrument, force_activate=False):
        # type: (InstrumentInterface, bool) -> Optional[Sequence]
        seq = Sequence()

        if force_activate or not instrument.activated:
            seq.add(instrument.device.track.select)
            seq.add(partial(self._device_service.make_plugin_window_showable, instrument.device))
            seq.add(lambda: setattr(instrument, "activated", True), name="mark instrument as activated")

        if force_activate or instrument.needs_exclusive_activation:
            seq.add(instrument.device.track.select)
            seq.add(instrument.exclusive_activate)

        if force_activate or not instrument.activated:
            seq.add(instrument.post_activate)

        return seq.done()

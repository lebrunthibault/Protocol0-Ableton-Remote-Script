from functools import partial

from typing import Optional

from protocol0.domain.lom.device.DeviceDisplayService import DeviceDisplayService
from protocol0.domain.lom.instrument.InstrumentActivatedEvent import InstrumentActivatedEvent
from protocol0.domain.lom.instrument.InstrumentSelectedEvent import InstrumentSelectedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentDisplayService(object):
    def __init__(self, device_display_service):
        # type: (DeviceDisplayService) -> None
        self._device_display_service = device_display_service
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._on_simple_track_armed_event)
        DomainEventBus.subscribe(InstrumentSelectedEvent, self._on_instrument_selected_event)

    def show_instrument(self, track):
        # type: (AbstractTrack) -> Optional[Sequence]
        if track.instrument is None or not track.instrument.CAN_BE_SHOWN:
            raise Protocol0Warning("Instrument cannot be shown")

        return self.activate_plugin_window(track.instrument_track, force_activate=True, slow=False)

    def _on_simple_track_armed_event(self, event):
        # type: (SimpleTrackArmedEvent) -> Optional[Sequence]
        track = SongFacade.simple_track_from_live_track(event.live_track)

        if (
            not SongFacade.current_track().instrument
            or SongFacade.current_track().instrument_track != track
        ):
            return None

        if not track.instrument or not track.instrument.needs_exclusive_activation:
            return None

        seq = Sequence()
        seq.add(
            partial(self.activate_plugin_window, track, force_activate=track.instrument.force_show)
        )
        # if not track.instrument.force_show:
        #     seq.add(Backend.client().hide_plugins)
        # track.instrument.force_show = False
        return seq.done()

    def _on_instrument_selected_event(self, _):
        # type: (InstrumentSelectedEvent) -> Optional[Sequence]
        return self.show_instrument(SongFacade.current_track())

    def activate_plugin_window(self, track, force_activate=False, slow=True):
        # type: (SimpleTrack, bool, bool) -> Optional[Sequence]
        seq = Sequence()
        instrument = track.instrument
        if instrument is None:
            Logger.warning("Instrument not found")
            return None

        seq.add(track.select)
        seq.add(
            partial(
                self._device_display_service.make_plugin_window_showable,
                track,
                instrument.device,
                slow=slow
            )
        )

        if force_activate or instrument.needs_exclusive_activation:
            seq.add(track.select)
            seq.add(instrument.exclusive_activate)

        if force_activate:
            seq.add(instrument.post_activate)

        seq.add(partial(DomainEventBus.emit, InstrumentActivatedEvent(instrument)))

        return seq.done()

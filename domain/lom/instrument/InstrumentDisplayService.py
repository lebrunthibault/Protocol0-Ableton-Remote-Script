from functools import partial

from typing import Optional

from protocol0.domain.lom.device.DeviceDisplayService import DeviceDisplayService
from protocol0.domain.lom.instrument.InstrumentActivatedEvent import InstrumentActivatedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentDisplayService(object):
    def __init__(self, device_display_service):
        # type: (DeviceDisplayService) -> None
        self._device_display_service = device_display_service
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._on_simple_track_armed_event)

    def show_hide_instrument(self, track):
        # type: (AbstractTrack) -> Optional[Sequence]
        if track.instrument is None or not track.instrument.CAN_BE_SHOWN:
            return None

        track = track.instrument_track

        seq = Sequence()
        if not track.instrument.activated or track.instrument.needs_exclusive_activation:
            seq.add(partial(self.activate_plugin_window, track))
        else:
            seq.add(track.select)
            if SongFacade.selected_track() != track:
                seq.add(Backend.client().show_plugins)
            else:
                seq.add(Backend.client().show_hide_plugins)
        return seq.done()

    def activate_instrument_plugin_window(self, track):
        # type: (AbstractTrack) -> None
        if track.instrument is None or not track.instrument.CAN_BE_SHOWN:
            return None

        self.activate_plugin_window(track.instrument_track, force_activate=True)

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
        seq.add(partial(self.activate_plugin_window, track))
        if not track.instrument.force_show:
            seq.add(Backend.client().hide_plugins)
        track.instrument.force_show
        return seq.done()

    def activate_plugin_window(self, track, force_activate=False):
        # type: (SimpleTrack, bool) -> Optional[Sequence]
        seq = Sequence()
        instrument = track.instrument
        assert instrument

        if force_activate or not instrument.activated:
            seq.add(track.select)
            seq.add(
                partial(
                    self._device_display_service.make_plugin_window_showable,
                    track,
                    instrument.device,
                )
            )
            seq.add(
                lambda: setattr(instrument, "activated", True), name="mark instrument as activated"
            )

        if force_activate or instrument.needs_exclusive_activation:
            seq.add(track.select)
            seq.add(instrument.exclusive_activate)

        if force_activate or not instrument.activated:
            seq.add(instrument.post_activate)

        seq.add(partial(DomainEventBus.emit, InstrumentActivatedEvent(instrument)))

        return seq.done()

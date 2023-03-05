from functools import partial

from typing import Optional, Union, cast

from protocol0.domain.lom.device.DeviceDisplayService import DeviceDisplayService
from protocol0.domain.lom.instrument.InstrumentActivatedEvent import InstrumentActivatedEvent
from protocol0.domain.lom.instrument.InstrumentSelectedEvent import InstrumentSelectedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackSaveStartedEvent import \
    SimpleTrackSaveStartedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence

RecordableTrack = Union[ExternalSynthTrack, SimpleTrack]


class InstrumentDisplayService(object):
    def __init__(self, device_display_service):
        # type: (DeviceDisplayService) -> None
        self._device_display_service = device_display_service
        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._on_simple_track_armed_event)
        DomainEventBus.subscribe(SimpleTrackSaveStartedEvent, self._on_simple_track_save_started_event)
        DomainEventBus.subscribe(InstrumentSelectedEvent, self._on_instrument_selected_event)

    def show_instrument(self, track):
        # type: (AbstractTrack) -> Optional[Sequence]
        if track.instrument is None or not track.instrument.CAN_BE_SHOWN:
            raise Protocol0Warning("Instrument cannot be shown")

        return self.activate_plugin_window(
            cast(RecordableTrack, track).instrument_track, force_activate=True
        )

    def _on_simple_track_armed_event(self, event):
        # type: (SimpleTrackArmedEvent) -> Optional[Sequence]
        track = Song.live_track_to_simple_track(event.live_track)

        current_track = Song.current_track()
        if (
            not isinstance(current_track, (ExternalSynthTrack, SimpleTrack))
            or current_track.instrument is None
            or current_track.instrument_track != track
        ):
            return None

        if not track.instrument or not track.instrument.needs_exclusive_activation:
            return None

        seq = Sequence()
        seq.add(partial(self.activate_plugin_window, track))
        seq.add(Backend.client().hide_plugins)

        return seq.done()

    def _on_simple_track_save_started_event(self, _):
        # type: (SimpleTrackSaveStartedEvent) -> Optional[Sequence]
        """Hide the plugin window so it does not reappear while freezing"""
        track = Song.selected_track()
        if track.instrument is None:  # e.g. minitaur
            return None

        assert track.instrument.device, "Flattening track has no instrument device"

        return self._device_display_service.toggle_plugin_window(
            track, track.instrument.device, activate=False
        )

    def _on_instrument_selected_event(self, _):
        # type: (InstrumentSelectedEvent) -> Optional[Sequence]
        return self.show_instrument(Song.current_track())

    def activate_plugin_window(self, track, force_activate=False):
        # type: (SimpleTrack, bool) -> Optional[Sequence]
        seq = Sequence()
        instrument = track.instrument
        if instrument is None:
            Logger.warning("Instrument not found")
            return None

        seq.add(track.select)
        seq.add(
            partial(
                self._device_display_service.toggle_plugin_window,
                track,
                instrument.device,
            )
        )

        if force_activate or instrument.needs_exclusive_activation:
            seq.add(track.select)
            seq.add(instrument.exclusive_activate)

        if force_activate:
            seq.add(instrument.post_activate)

        seq.add(partial(DomainEventBus.emit, InstrumentActivatedEvent(instrument)))

        return seq.done()

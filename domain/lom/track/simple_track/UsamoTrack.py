from typing import Any

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackArmedEvent import (
    ExternalSynthTrackArmedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.external_synth.ExternalSynthAudioRecordingEndedEvent import (
    ExternalSynthAudioRecordingEndedEvent,
)
from protocol0.domain.track_recorder.external_synth.ExternalSynthAudioRecordingStartedEvent import (
    ExternalSynthAudioRecordingStartedEvent,
)
from protocol0.shared.SongFacade import SongFacade


class UsamoTrack(SimpleMidiTrack):
    """
    This track holds the usamo device that I enabled
    when I'm recording audio (to have sample accurate audio)
    """

    TRACK_NAME = "Usamo"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(UsamoTrack, self).__init__(*a, **k)
        self._usamo_device = self.devices.get_one_from_enum(DeviceEnum.USAMO)
        if self._usamo_device is None:
            raise Protocol0Error("Cannot find usamo device on usamo track")

        DomainEventBus.subscribe(SimpleTrackArmedEvent, self._on_simple_track_armed_event)
        DomainEventBus.subscribe(
            ExternalSynthTrackArmedEvent, self._on_external_synth_track_armed_event
        )
        DomainEventBus.subscribe(
            ExternalSynthAudioRecordingStartedEvent,
            self._on_external_synth_audio_recording_started_event,
        )
        DomainEventBus.subscribe(
            ExternalSynthAudioRecordingEndedEvent,
            self._on_external_synth_audio_recording_ended_event,
        )

    def activate(self):
        # type: () -> None
        self._usamo_device.is_enabled = True

    def inactivate(self):
        # type: () -> None
        self._usamo_device.is_enabled = False

    def _on_simple_track_armed_event(self, event):
        # type: (SimpleTrackArmedEvent) -> None
        track = SongFacade.simple_track_from_live_track(event.live_track)
        if isinstance(track.abstract_track, ExternalSynthTrack):
            return None

        self.inactivate()

    def _on_external_synth_track_armed_event(self, event):
        # type: (ExternalSynthTrackArmedEvent) -> None
        if event.arm:
            # noinspection PyUnresolvedReferences
            self.input_routing.track = event.track.abstract_track.midi_track
            self.activate()  # this is the default: overridden by rev2
        else:
            self.inactivate()

    def _on_external_synth_audio_recording_started_event(self, _):
        # type: (ExternalSynthAudioRecordingStartedEvent) -> None
        self.activate()

    def _on_external_synth_audio_recording_ended_event(self, _):
        # type: (ExternalSynthAudioRecordingEndedEvent) -> None
        self.inactivate()

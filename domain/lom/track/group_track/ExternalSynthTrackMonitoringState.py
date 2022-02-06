from typing import Any, TYPE_CHECKING

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.SongFacade import SongFacade
from protocol0.infra.scheduler.Scheduler import Scheduler

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ExternalSynthTrackMonitoringState(object):
    def __init__(self, track, *a, **k):
        # type: (ExternalSynthTrack, Any, Any) -> None
        super(ExternalSynthTrackMonitoringState, self).__init__(*a, **k)
        self._track = track

    def switch(self):
        # type: () -> None
        if self._monitors_midi:
            self.monitor_audio()
        else:
            self.monitor_midi()

    @property
    def _monitors_midi(self):
        # type: () -> bool
        return self._track.midi_track.mute is False

    # noinspection DuplicatedCode
    def monitor_midi(self):
        # type: () -> None
        # midi track
        self._un_mute_track(self._track.midi_track)
        self._track.midi_track.input_routing.type = self._track.instrument.MIDI_INPUT_ROUTING_TYPE
        for midi_clip in self._track.midi_track.clips:
            audio_clip = self._track.audio_track.clip_slots[midi_clip.index].clip
            # do not unmute muted clip slot
            if audio_clip and audio_clip.muted:
                continue
            midi_clip.muted = False
            if audio_clip.is_playing:
                Scheduler.defer(SongFacade.scenes()[midi_clip.index].fire)

        # audio track
        self._mute_track(self._track.audio_track)
        self._track.audio_track._output_meter_level_listener.subject = self._track.audio_track._track

        # audio tail track
        if self._track.audio_tail_track:
            self._mute_track(self._track.audio_tail_track)

        # switch solo
        if self._track.audio_track.solo:
            self._track.midi_track.solo = True
            self._track.audio_track.solo = False

        # external device
        if self._track._external_device:
            self._track._external_device.device_on = True

    # noinspection DuplicatedCode
    def monitor_audio(self):
        # type: () -> None
        # midi track
        self._mute_track(self._track.midi_track)
        for clip in self._track.midi_track.clips:
            clip.muted = True

        # audio track
        self._un_mute_track(self._track.audio_track)
        self._track.audio_track._output_meter_level_listener.subject = None

        # audio tail track
        if self._track.audio_tail_track:
            self._un_mute_track(self._track.audio_tail_track)

        # switch solo
        if self._track.midi_track.solo:
            self._track.audio_track.solo = True
            self._track.midi_track.solo = False

        # external device
        if self._track._external_device:
            self._track._external_device.device_on = False

    def _mute_track(self, track):
        # type: (SimpleTrack) -> None
        track.mute = True
        track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        track.output_routing.type = OutputRoutingTypeEnum.SENDS_ONLY

    def _un_mute_track(self, track):
        # type: (SimpleTrack) -> None
        track.mute = False
        track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        track.output_routing.track = track.group_track

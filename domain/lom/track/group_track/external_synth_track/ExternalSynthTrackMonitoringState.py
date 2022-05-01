from typing import TYPE_CHECKING

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack


class ExternalSynthTrackMonitoringState(object):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        super(ExternalSynthTrackMonitoringState, self).__init__()
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
        return self._track.midi_track.muted is False

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
            if audio_clip and audio_clip.is_playing and SongFacade.is_playing() and not SongFacade.is_recording():
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
        self._track._external_device.is_enabled = True

    # noinspection DuplicatedCode
    def monitor_audio(self):
        # type: () -> None
        # midi track
        self._mute_track(self._track.midi_track)

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
        self._track._external_device.is_enabled = False

    def _mute_track(self, track):
        # type: (SimpleTrack) -> None
        track.muted = True
        track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        track.output_routing.type = OutputRoutingTypeEnum.SENDS_ONLY

    def _un_mute_track(self, track):
        # type: (SimpleTrack) -> None
        track.muted = False
        track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        output_track = track.group_track
        if len(self._track.dummy_tracks):
            output_track = self._track.dummy_tracks[0]

        track.output_routing.track = output_track  # type: ignore[assignment]

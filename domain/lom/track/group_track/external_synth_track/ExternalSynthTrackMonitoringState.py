from typing import List, Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


class ExternalSynthTrackMonitoringState(object):
    def __init__(self,
                 midi_track,  # type: SimpleMidiTrack
                 audio_track,  # type: SimpleAudioTrack
                 audio_tail_track,  # type: Optional[SimpleAudioTailTrack]
                 dummy_tracks,  # type: List[SimpleDummyTrack]
                 external_device,  # type: Device
                 ):
        # type: (...) -> None
        self._midi_track = midi_track
        self._audio_track = audio_track
        self._audio_tail_track = audio_tail_track
        self._dummy_tracks = dummy_tracks
        self._external_device = external_device

    def switch(self):
        # type: () -> None
        if self._monitors_midi:
            self.monitor_audio()
        else:
            if self._midi_track.arm_state.is_armed:
                self.monitor_midi()
            else:
                raise Protocol0Warning("Please arm the track first")

    @property
    def _monitors_midi(self):
        # type: () -> bool
        return self._midi_track.muted is False

    def monitor_midi(self):
        # type: () -> None
        # midi track
        self._un_mute_track(self._midi_track)

        # for midi_clip in self._midi_track.clips:
        #     audio_clip = list(self._audio_track.clip_slots)[midi_clip.index].clip
        #     # do not unmute muted clip slot
        #     if audio_clip and audio_clip.muted:
        #         continue
        #     midi_clip.muted = False
        #     # if audio_clip and audio_clip.is_playing and SongFacade.is_playing():
        #     #     Scheduler.defer(SongFacade.scenes()[midi_clip.index].fire)

        # audio track
        self._mute_track(self._audio_track)
        self._audio_track._output_meter_level_listener.subject = self._audio_track._track

        # audio tail track
        if self._audio_tail_track:
            self._mute_track(self._audio_tail_track)

        # switch solo
        if self._audio_track.solo:
            self._midi_track.solo = True
            self._audio_track.solo = False

        # external device
        self._external_device.is_enabled = True

    # noinspection DuplicatedCode
    def monitor_audio(self):
        # type: () -> None
        # midi track
        self._mute_track(self._midi_track)

        # audio track
        self._un_mute_track(self._audio_track)
        self._audio_track._output_meter_level_listener.subject = None

        # audio tail track
        if self._audio_tail_track:
            self._un_mute_track(self._audio_tail_track)

        # switch solo
        if self._midi_track.solo:
            self._audio_track.solo = True
            self._midi_track.solo = False

        # external device
        self._external_device.is_enabled = False

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
        if len(self._dummy_tracks):
            output_track = self._dummy_tracks[0]

        if output_track:
            track.output_routing.track = output_track

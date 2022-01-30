from typing import Any, TYPE_CHECKING

from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ExternalSynthTrackMonitoringState(AbstractObject):
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
        self._track.midi_track.mute = False
        self._track.midi_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        self._track.midi_track.input_routing_type = self._track.instrument.MIDI_INPUT_ROUTING_TYPE
        for midi_clip in self._track.midi_track.clips:
            audio_clip = self._track.audio_track.clip_slots[midi_clip.index].clip
            # do not unmute muted clip slot
            if audio_clip and audio_clip.muted:
                continue
            midi_clip.muted = False
            if audio_clip.is_playing:
                self.parent.defer(self.song.scenes[midi_clip.index].fire)

        # audio track
        self._track.audio_track.mute = True
        self._track.audio_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        # checking levels
        self._track.audio_track._output_meter_level_listener.subject = self._track.audio_track._track

        # audio tail track
        if self._track.audio_tail_track:
            self._track.audio_tail_track.mute = True
            self._track.audio_tail_track.current_monitoring_state = CurrentMonitoringStateEnum.IN

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
        self._track.midi_track.mute = True
        self._track.midi_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        for clip in self._track.midi_track.clips:
            clip.muted = True

        # audio track
        self._track.audio_track.mute = False
        self._track.audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        self._track.audio_track._output_meter_level_listener.subject = None

        # audio tail track
        if self._track.audio_tail_track:
            self._track.audio_tail_track.mute = False
            self._track.audio_tail_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

        # switch solo
        if self._track.midi_track.solo:
            self._track.audio_track.solo = True
            self._track.midi_track.solo = False

        # external device
        if self._track._external_device:
            self._track._external_device.device_on = False

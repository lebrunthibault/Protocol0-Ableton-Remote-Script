from typing import List

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.recorder.track_recorder_external_synth_mixin import TrackRecorderExternalSynthMixin


class TrackRecorderExternalSynth(TrackRecorderExternalSynthMixin, AbstractTrackRecorder):
    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.midi_track, self.track.audio_track, self.track.audio_tail_track])

    def post_audio_record(self):
        # type: () -> None
        super(TrackRecorderExternalSynth, self).post_audio_record()
        self.track.audio_track.clip_slots[self.recording_scene_index].clip.color = ClipColorEnum.AUDIO_UN_QUANTIZED.color_int_value

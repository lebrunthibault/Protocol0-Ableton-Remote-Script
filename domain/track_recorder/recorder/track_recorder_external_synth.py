from typing import List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.recorder.track_recorder_external_synth_mixin import TrackRecorderExternalSynthMixin


class TrackRecorderExternalSynth(TrackRecorderExternalSynthMixin, AbstractTrackRecorder):
    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.midi_track, self.track.audio_track, self.track.audio_tail_track])

from typing import List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.external_synth.track_recorder_external_synth_normal import \
    TrackRecorderExternalSynthNormal
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthNormalUnlimited(TrackRecorderExternalSynthNormal):
    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return filter(None, [self.track.midi_track, self.track.audio_track])

    def record(self, bar_length):
        # type: (float) -> Sequence
        self.track.audio_tail_track.unarm()
        return super(TrackRecorderExternalSynthNormalUnlimited, self).record(bar_length)

from typing import List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder


class TrackRecorderSimple(AbstractTrackRecorder):
    @property
    def track(self):
        # type: (AbstractTrackRecorder) -> SimpleTrack
        # noinspection PyTypeChecker
        return self._track

    @property
    def _main_recording_track(self):
        # type: () -> SimpleTrack
        return self.track

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return [self.track]

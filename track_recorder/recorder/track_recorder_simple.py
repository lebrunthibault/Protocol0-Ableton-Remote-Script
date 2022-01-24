from typing import List

from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder


class TrackRecorderSimple(AbstractTrackRecorder):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        super(TrackRecorderSimple, self).__init__(track=track)
        self.track = track

    @property
    def _main_recording_track(self):
        # type: () -> SimpleTrack
        return self.track

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        return [self.track]

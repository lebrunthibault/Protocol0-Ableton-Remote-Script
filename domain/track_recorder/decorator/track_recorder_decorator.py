from typing import TYPE_CHECKING

from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackRecorderDecorator(AbstractTrackRecorder):
    def __init__(self, recorder, song):
        # type: (AbstractTrackRecorder, Song) -> None
        super(TrackRecorderDecorator, self).__init__(track=recorder.track, song=song)
        self.recorder = recorder
        self._track = recorder.track

    @property
    def recording_scene_index(self):
        # type: () -> int
        return self.recorder.recording_scene_index

    def set_recording_scene_index(self, recording_scene_index):
        # type: (int) -> None
        self.recorder.set_recording_scene_index(recording_scene_index)

    def pre_record(self):
        # type: () -> Sequence
        return self.recorder.pre_record()

    def record(self, bar_length):
        # type: (int) -> Sequence
        return self.recorder.record(bar_length)

    def post_audio_record(self):
        # type: () -> None
        return self.recorder.post_audio_record()

    def post_record(self, bar_length):
        # type: (int) -> None
        return self.recorder.post_record(bar_length)

    def cancel_record(self):
        # type: () -> None
        return self.recorder.cancel_record()

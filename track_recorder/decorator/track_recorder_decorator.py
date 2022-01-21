from typing import Optional

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.sequence.Sequence import Sequence


class TrackRecorderDecorator(AbstractTrackRecorder, AbstractObject):
    def __init__(self, recorder):
        # type: (AbstractTrackRecorder) -> None
        super(TrackRecorderDecorator, self).__init__(track=recorder.track)
        self.recorder = recorder
        self.track = recorder.track

    @property
    def recording_scene_index(self):
        # type: () -> int
        return self.recorder.recording_scene_index

    def pre_record(self):
        # type: () -> Optional[Sequence]
        return self.recorder.pre_record()

    def record(self, bar_length):
        # type: (int) -> Sequence
        return self.recorder.record(bar_length)

    def post_record(self, errored=False):
        # type: (bool) -> None
        return self.recorder.post_record(errored)

    def cancel_record(self):
        # type: () -> None
        return self.recorder.cancel_record()

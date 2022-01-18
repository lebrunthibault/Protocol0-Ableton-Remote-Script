from typing import Optional

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface
from protocol0.sequence.Sequence import Sequence


class TrackRecorderDecorator(TrackRecorderInterface, AbstractObject):
    def __init__(self, recorder):
        # type: (TrackRecorderInterface) -> None
        super(TrackRecorderDecorator, self).__init__(track=recorder.track)
        self.recorder = recorder
        self.track = recorder.track

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        return self.recorder.next_empty_clip_slot_index

    def pre_record(self):
        # type: () -> Sequence
        return self.recorder.pre_record()

    def record(self, bar_length):
        # type: (int) -> Sequence
        return self.recorder.record(bar_length=bar_length)

    def post_record(self):
        # type: () -> None
        return self.recorder.post_record()

    def on_record_cancelled(self):
        # type: () -> Sequence
        return self.recorder.on_record_cancelled()

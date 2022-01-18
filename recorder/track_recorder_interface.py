from typing import Optional

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.sequence.Sequence import Sequence


class TrackRecorderInterface(AbstractObject):
    def __init__(self, track):
        # type: (AbstractTrack) -> None
        super(TrackRecorderInterface, self).__init__()
        self.track = track

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        raise NotImplementedError

    def pre_record(self):
        # type: () -> Sequence
        pass

    def record(self, bar_length):
        # type: (int) -> Sequence
        raise NotImplementedError

    def post_record(self):
        # type: () -> None
        pass

    def on_record_cancelled(self):
        # type: () -> Sequence
        raise NotImplementedError

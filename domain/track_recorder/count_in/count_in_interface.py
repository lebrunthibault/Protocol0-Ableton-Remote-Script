from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.sequence.Sequence import Sequence


class CountInInterface(AbstractObject):
    def __init__(self, track):
        # type: (AbstractTrack) -> None
        super(CountInInterface, self).__init__()
        self.track = track

    def launch(self):
        # type: () -> Sequence
        raise NotImplementedError
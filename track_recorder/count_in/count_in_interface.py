from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.sequence.Sequence import Sequence


class CountInInterface(AbstractObject):
    def __init__(self, track):
        # type: (AbstractTrack) -> None
        super(CountInInterface, self).__init__()
        self.track = track

    def launch(self):
        # type: () -> Sequence
        raise NotImplementedError

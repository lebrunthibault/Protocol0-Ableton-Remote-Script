from protocol0.lom.AbstractObject import AbstractObject
from protocol0.sequence.Sequence import Sequence


class CountInInterface(AbstractObject):
    def launch(self):
        # type: () -> Sequence
        raise NotImplementedError

from typing import TYPE_CHECKING

from a_protocol_0.sequence.SequenceState import SequenceState

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.sequence.Sequence import Sequence


class SequenceError(Exception):
    def __init__(self, sequence, message="a sequence error occurred"):
        # type: (Sequence, str) -> None

        from a_protocol_0.sequence.Sequence import Sequence
        if not isinstance(sequence, Sequence):
            raise Exception("You didn't pass the sequence parameter to SequenceError")

        self.sequence = sequence
        self.message = message

        sequence._state = SequenceState.ERRORED
        super(Exception, self).__init__("%s, (%s)" % (str(self.message), sequence))

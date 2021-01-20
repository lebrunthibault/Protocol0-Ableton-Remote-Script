from typing import TYPE_CHECKING, Union

from a_protocol_0.errors.Protocol0Error import Protocol0Error

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.sequence.Sequence import Sequence
    from a_protocol_0.sequence.SequenceStep import SequenceStep


class SequenceError(RuntimeError):
    def __init__(self, object, message="a sequence error occurred"):
        # type: (Union[Sequence, SequenceStep], str) -> None

        from a_protocol_0.sequence.Sequence import Sequence
        from a_protocol_0.sequence.SequenceStep import SequenceStep
        if not isinstance(object, Sequence) and not isinstance(object, SequenceStep):
            raise Protocol0Error("You didn't pass an appropriate object parameter to SequenceError")

        object._errored = True
        super(RuntimeError, self).__init__("%s, (%s)" % (str(message), object))

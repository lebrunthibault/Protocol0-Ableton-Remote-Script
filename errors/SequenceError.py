from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.sequence.Sequence import Sequence


class SequenceError(RuntimeError):
    pass

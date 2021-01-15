from typing import TYPE_CHECKING, List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.utils import get_callable_name

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.sequence.Sequence import Sequence


class ParallelSequenceStep(AbstractControlSurfaceComponent):
    def __init__(self, funcs, sequence, wait=None, name=None, complete_on=None,
                 do_if=None, do_if_not=None, return_if=None, return_if_not=None, check_timeout=5, *a, **k):
        # type: (callable, Sequence, float, str, callable, bool) -> None
        """ the tick is 100 ms """
        self.callables = funcs  # type: List[callable]

    def __repr__(self):
        return "%s (and %s more)" % (get_callable_name(self.callables[0]), len(self.callables) - 1)

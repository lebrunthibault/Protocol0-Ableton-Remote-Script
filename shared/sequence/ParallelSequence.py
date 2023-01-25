from collections import deque

from _Framework.SubjectSlot import SlotManager
from typing import List, Callable

from protocol0.domain.shared.utils.func import get_callable_repr
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.SequenceState import SequenceState
from protocol0.shared.sequence.SequenceStep import SequenceStep
from protocol0.shared.sequence.SequenceTransition import SequenceStateEnum


class ParallelSequence(SlotManager, Observable):
    """executes steps in parallel"""

    def __init__(self, funcs):
        # type: (List[Callable]) -> None
        super(ParallelSequence, self).__init__()
        self._steps = deque([SequenceStep(func, get_callable_repr(func), True) for func in funcs])
        self._steps_terminated_count = 0
        self.state = SequenceState()
        self.res = None

    def __repr__(self):
        # type: () -> str
        return "ParallelSequence(%s / %s)" % (self._steps_terminated_count, len(self._steps))

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, SequenceStep):
            if observable.state.terminated:
                self._steps_terminated_count += 1
                self._check_for_parallel_step_completion()
                observable.remove_observer(self)

    def start(self):
        # type: () -> ParallelSequence
        if not self.state.started and not self.state.terminated:
            self.state.change_to(SequenceStateEnum.STARTED)

        if len(self._steps) == 0:
            self._check_for_parallel_step_completion()

        for step in self._steps:
            step.register_observer(self)
            step.start()

        return self

    def _check_for_parallel_step_completion(self):
        # type: () -> None
        if self._steps_terminated_count == len(self._steps) and not self.state.terminated:
            self.state.change_to(SequenceStateEnum.TERMINATED)
            self.notify_observers()
            self.disconnect()

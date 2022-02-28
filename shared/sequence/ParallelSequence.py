from collections import deque

from _Framework.SubjectSlot import subject_slot_group
from typing import List, Callable

from protocol0.domain.shared.utils import get_callable_repr
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStep import SequenceStep


class ParallelSequence(Sequence):
    """ executes steps in parallel """
    def __init__(self, funcs):
        # type: (List[Callable]) -> None
        super(ParallelSequence, self).__init__()
        self._steps = deque([SequenceStep(func, get_callable_repr(func), False) for func in funcs])
        self._steps_terminated_count = 0

    def start(self):
        # type: () -> ParallelSequence
        self.change_state(SequenceStateEnum.STARTED)
        for step in self._steps:  # type: SequenceStep
            self._parallel_step_termination.add_subject(step)
            step.start()

        self._check_for_parallel_step_completion()
        return self

    @subject_slot_group("terminated")
    def _parallel_step_termination(self, _):
        # type: (Sequence) -> None
        self._steps_terminated_count += 1
        self._check_for_parallel_step_completion()

    def _check_for_parallel_step_completion(self):
        # type: () -> None
        if self._steps_terminated_count == len(self._steps):
            self._terminate()

from collections import deque

from _Framework.SubjectSlot import subject_slot_group
from typing import List, Callable

from protocol0.domain.shared.utils import get_callable_repr
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.shared.sequence.SequenceStep import SequenceStep


class ParallelSequence(SequenceStateMachineMixin):
    """ executes steps in parallel """
    __subject_events__ = ("terminated",)

    def __init__(self, funcs):
        # type: (List[Callable]) -> None
        super(ParallelSequence, self).__init__()
        self._steps = deque([SequenceStep(func, get_callable_repr(func), True) for func in funcs])
        self._steps_terminated_count = 0

    def start(self):
        # type: () -> ParallelSequence
        self.change_state(SequenceStateEnum.STARTED)
        self._check_for_parallel_step_completion()
        for step in self._steps:
            self._parallel_step_termination.add_subject(step)
            step.start()

        return self

    @subject_slot_group("terminated")
    def _parallel_step_termination(self, _):
        # type: (SequenceStep) -> None
        self._steps_terminated_count += 1
        self._check_for_parallel_step_completion()

    def _check_for_parallel_step_completion(self):
        # type: () -> None
        if self._steps_terminated_count == len(self._steps):
            self.change_state(SequenceStateEnum.TERMINATED)
            self.notify_terminated()  # type: ignore[attr-defined]
            self.disconnect()

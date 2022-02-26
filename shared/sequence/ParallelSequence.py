from functools import partial

from _Framework.SubjectSlot import subject_slot_group
from typing import List, Callable

from protocol0.shared.sequence.Sequence import Sequence
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStep import SequenceStep


class ParallelSequence(Sequence):
    """ executes steps in parallel """
    def __init__(self):
        # type: () -> None
        super(ParallelSequence, self).__init__()
        self._steps_terminated_count = 0

    @classmethod
    def make_func_from_list(cls, funcs):
        # type: (List[Callable]) -> Callable
        def parallel_sequence_creator(callbacks):
            # type: (List[Callable]) -> Sequence

            seq = ParallelSequence()
            [seq.add(func) for func in callbacks]
            return seq.done()

        return partial(parallel_sequence_creator, funcs)

    def start(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.STARTED)
        if len(self._steps) == 0:
            self._check_for_parallel_step_completion()
            return
        for step in self._steps:  # type: SequenceStep
            self._parallel_step_termination.add_subject(step)
            step.start()

    @subject_slot_group("terminated")
    def _parallel_step_termination(self, _):
        # type: (Sequence) -> None
        self._steps_terminated_count += 1
        self._check_for_parallel_step_completion()

    def _check_for_parallel_step_completion(self):
        # type: () -> None
        if self._steps_terminated_count == len(self._steps):
            self._terminate()

    def _terminate(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.TERMINATED)
        self.notify_terminated()  # type: ignore[attr-defined]
        self.disconnect()

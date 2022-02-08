from _Framework.SubjectSlot import subject_slot_group
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.shared.sequence.SequenceStep import SequenceStep


class ParallelSequence(Sequence):
    """ executes steps in parallel """

    def __init__(self):
        # type: () -> None
        super(ParallelSequence, self).__init__()
        self._steps_terminated_count = 0

    def _on_start(self):
        # type: () -> None
        if len(self._steps) == 0:
            self.check_for_parallel_step_completion()
            return
        for step in self._steps:  # type: SequenceStep
            self._parallel_step_termination.add_subject(step)
            step.start()

    @subject_slot_group("terminated")
    def _parallel_step_termination(self, _):
        # type: (Sequence) -> None
        self._steps_terminated_count += 1
        self.check_for_parallel_step_completion()

    def check_for_parallel_step_completion(self):
        # type: () -> None
        if self._steps_terminated_count == len(self._steps):
            self.terminate()

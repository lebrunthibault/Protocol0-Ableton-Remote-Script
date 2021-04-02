from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.sequence.SequenceStep import SequenceStep


class ParallelSequence(Sequence):
    """ executes steps in parallel """
    def __init__(self, *a, **k):
        # type: (callable, Sequence, float, str, callable, bool) -> None
        super(ParallelSequence, self).__init__(*a, **k)
        self._steps_terminated_count = 0

    def _start(self):
        for step in self._steps:  # type: SequenceStep
            self._parallel_step_termination.add_subject(step)
            step.start()

    @subject_slot_group("terminated")
    def _parallel_step_termination(self, value):
        self._steps_terminated_count += 1
        self.check_for_parallel_step_completion()

    def check_for_parallel_step_completion(self):
        if self._steps_terminated_count == len(self._steps):
            self._res = True
            # noinspection PyUnresolvedReferences
            self.notify_terminated()

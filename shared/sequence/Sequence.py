from collections import deque

from typing import Deque, Optional, Iterable, Union, Callable, Any, List

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.utils import get_frame_info, nop, get_callable_repr
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.SequenceActionMixin import SequenceActionMixin
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.shared.sequence.SequenceStep import SequenceStep


class Sequence(UseFrameworkEvents, SequenceStateMachineMixin, SequenceActionMixin):
    __subject_events__ = ("terminated",)
    """
    Replacement of the _Framework Task.
    I added asynchronous behavior by hooking in the listener system and my own event system,
    including communication with the backend
    Encapsulates and composes all asynchronous tasks done in the script.
    """
    RUNNING_SEQUENCES = []  # type: List[Sequence]
    _DEBUG = False

    def __init__(self):
        # type: () -> None
        super(Sequence, self).__init__()

        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: Optional[SequenceStep]
        self.res = None  # type: Optional[Any]
        frame_info = get_frame_info(2)
        if frame_info:
            self.name = "[seq %s.%s]" % (frame_info.class_name, frame_info.method_name)
        else:
            self.name = "Unknown"

    def __repr__(self, **k):
        # type: (Any) -> str
        return self.name

    def add(self, func=nop, name=None, notify_terminated=True):
        # type: (Union[Iterable, Callable, object], str, bool) -> None
        """ callback can be a callable or a list of callable (will execute in parallel) """
        assert callable(func) or isinstance(func, Iterable), "You passed a non callable (%s) to %s" % (func, self)
        if isinstance(func, List):
            from protocol0.shared.sequence.ParallelSequence import ParallelSequence
            func = ParallelSequence(func).start

        step_name = "%s : step %s" % (self.name, name or get_callable_repr(func))

        step = SequenceStep(func, step_name, notify_terminated)
        self._steps.append(step)

    def done(self):
        # type: () -> Sequence
        self.change_state(SequenceStateEnum.STARTED)
        self.RUNNING_SEQUENCES.append(self)
        self._execute_next_step()
        return self

    def _execute_next_step(self):
        # type: () -> None
        if not self.started:
            return
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self._DEBUG:
                Logger.log_debug("Executing %s : %s" % (self, self._current_step))
            self._step_terminated.subject = self._current_step
            self._step_errored.subject = self._current_step
            self._step_cancelled.subject = self._current_step
            self._current_step.start()
        else:
            self._terminate()

    @classmethod
    def restart(cls):
        # type: () -> None
        for seq in reversed(Sequence.RUNNING_SEQUENCES):
            seq._cancel()
        Sequence.RUNNING_SEQUENCES = []

    @p0_subject_slot("terminated")
    def _step_terminated(self):
        # type: () -> None
        if self._DEBUG:
            Logger.log_info("step terminated : %s" % self._current_step)
        self._execute_next_step()

    @p0_subject_slot("errored")
    def _step_errored(self):
        # type: () -> None
        self._error()

    def _error(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.ERRORED)
        self.disconnect()
        if self._DEBUG:
            Logger.log_error("%s" % self, debug=False)

    @p0_subject_slot("cancelled")
    def _step_cancelled(self):
        # type: () -> None
        self._cancel()

    def _cancel(self):
        # type: () -> None
        if self.started:
            self.change_state(SequenceStateEnum.CANCELLED)
            Logger.log_warning("%s has been cancelled" % self)
            if self._current_step:
                self._current_step.cancel()
            self.disconnect()

    def _terminate(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.TERMINATED)

        self.res = self._current_step.res if self._current_step else None
        self.notify_terminated()  # type: ignore[attr-defined]
        self.disconnect()

    def disconnect(self):
        # type: () -> None
        super(Sequence, self).disconnect()
        try:
            self.RUNNING_SEQUENCES.remove(self)
        except ValueError:
            pass

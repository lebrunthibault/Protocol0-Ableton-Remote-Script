from collections import deque

from typing import Deque, Optional, Iterable, Union, Callable, Any, List

from protocol0.config import Config
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin, SequenceState
from protocol0.sequence.SequenceStep import SequenceStep
from protocol0.utils.decorators import p0_subject_slot
from protocol0.utils.utils import get_frame_info, nop


class Sequence(AbstractObject, SequenceStateMachineMixin):
    """
    Replacement of the _Framework Task as it does not seem to allow variable timeouts like triggers from listeners.
    See google doc for details.
    """

    __subject_events__ = ("terminated", "errored")

    RUNNING_SEQUENCES = []  # type: List[Sequence]

    def __init__(self, bypass_errors=False, silent=True, *a, **k):
        # type: (bool, bool, Any, Any) -> None
        super(Sequence, self).__init__(*a, **k)

        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: Optional[SequenceStep]
        self._bypass_errors = bypass_errors
        self.res = None  # type: Optional[Any]
        self.debug = Config.SEQUENCE_DEBUG or not silent
        frame_info = get_frame_info(2)
        if frame_info:
            self.name = "[seq %s.%s]" % (frame_info.class_name, frame_info.method_name)
        else:
            self.name = "Unknown"

    def __repr__(self):
        # type: () -> str
        return self.name

    @property
    def debug_str(self):
        # type: () -> str
        message = "%s in state %s" % (self, self.state)
        if not self._current_step:
            message += " (empty seq)"
        if self.res:
            message += " (res %s)" % self.res
        return message

    def _on_start(self):
        # type: () -> None
        self.RUNNING_SEQUENCES.append(self)
        self._execute_next_step()

    def _execute_next_step(self):
        # type: () -> None
        if self.has_final_state:
            return
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self.debug and self._current_step.debug:
                self.parent.log_debug("%s : %s" % (self, self._current_step), debug=False)
            self._step_terminated.subject = self._current_step
            self._step_errored.subject = self._current_step
            self._current_step.start()
        else:
            self.terminate()

    @p0_subject_slot("terminated")
    def _step_terminated(self):
        # type: () -> None
        if self._current_step.early_returned:
            self.terminate()
        else:
            self._execute_next_step()

    @p0_subject_slot("errored")
    def _step_errored(self):
        # type: () -> None
        if not self._bypass_errors:
            self.error()

    def _on_terminate(self):
        # type: () -> None
        try:
            self.RUNNING_SEQUENCES.remove(self)
        except ValueError:
            pass
        self.res = self._current_step.res if self._current_step else None

        if self.errored and self.debug:
            self.parent.log_error(self.debug_str, debug=False)

    def add(
            self,
            func=nop,  # type: Union[Iterable, Callable, object]
            wait=None,  # type: int
            name=None,  # type: str
            complete_on=None,  # type: Callable
            do_if=None,  # type: Callable
            return_if=None,  # type: Callable
            check_timeout=4,  # type: int
            no_timeout=False,  # type: bool
            silent=False,  # type: bool
    ):
        # type: (...) -> Sequence
        """
        check_timeout is the number of (exponential duration) checks executed before step failure
        (based on the Live.Base.Timer tick)
        callback can be :
        - not given (nop): can be used to just wait on a condition
        - a callable or a list of callable (parallel sequence execution) which are added as SequenceStep
        """
        assert callable(func) or isinstance(func, Iterable), "You passed a non callable (%s) to %s" % (
            func,
            self,
        )
        assert not self.terminated and not self.errored
        assert not isinstance(func, Sequence), "You passed a Sequence object instead of a Sequence factory to add"

        self._steps.append(
            SequenceStep.make(
                self,
                func,
                wait=wait,
                name=name,
                complete_on=complete_on,
                do_if=do_if,
                return_if=return_if,
                check_timeout=0 if no_timeout else check_timeout,
                silent=silent,
            )
        )

        return self

    def done(self):
        # type: () -> Sequence
        if self.state != str(SequenceState.UN_STARTED):
            raise Protocol0Error("Sequence done already called")
        self.start()
        return self

from collections import deque

from typing import Deque, Optional, Iterable, Union

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from a_protocol_0.sequence.SequenceStep import SequenceStep
from a_protocol_0.utils.decorators import p0_subject_slot
from a_protocol_0.utils.utils import get_frame_info, nop


class Sequence(AbstractObject, SequenceStateMachineMixin):
    """
    Replacement of the _Framework Task as it does not seem to allow variable timeouts like triggers from listeners.
    See google doc for details.
    """

    __subject_events__ = ("terminated", "errored")

    DEBUG_MODE = False
    SILENT_MODE = True

    def __init__(self, bypass_errors=False, silent=False, *a, **k):
        super(Sequence, self).__init__(*a, **k)

        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: Optional[SequenceStep]
        self._bypass_errors = bypass_errors
        self.res = None
        self.debug = self.DEBUG_MODE or not (silent or self.SILENT_MODE)
        frame_info = get_frame_info(2)
        self.name = "[seq %s.%s]" % (frame_info.class_name, frame_info.method_name) if frame_info else "Unknown"

    def __repr__(self):
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

    def __len__(self):
        return len(self._steps)

    def _on_start(self):
        self._execute_next_step()

    def _execute_next_step(self):
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self.debug and self._current_step.debug:
                self.parent.log_info("%s : %s" % (self, self._current_step), debug=False)
            self._step_terminated.subject = self._current_step
            self._step_errored.subject = self._current_step
            self._current_step.start()
        else:
            self.terminate()

    @p0_subject_slot("terminated")
    def _step_terminated(self):
        if self._current_step.early_returned:
            self.terminate()
        else:
            self._execute_next_step()

    @p0_subject_slot("errored")
    def _step_errored(self):
        if not self._bypass_errors:
            self.error()

    def _on_terminate(self):
        self.res = self._current_step.res if self._current_step else None

        if self.errored and self.debug:
            self.parent.log_error(self.debug_str, debug=False)

    def add(
        self,
        func=nop,  # type: Union[Iterable, callable]
        wait=None,
        name=None,
        complete_on=None,
        do_if=None,
        do_if_not=None,
        return_if=None,
        return_if_not=None,
        check_timeout=4,
        no_timeout=False,
        silent=False,
    ):
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
                do_if_not=do_if_not,
                return_if=return_if,
                return_if_not=return_if_not,
                check_timeout=0 if no_timeout else check_timeout,
                silent=silent,
            )
        )

        return self

    def done(self):
        # type: () -> Sequence
        self.start()
        return self

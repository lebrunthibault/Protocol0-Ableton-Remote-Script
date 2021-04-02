from collections import deque

from typing import List, Deque, Optional

from a_protocol_0.errors.SequenceError import SequenceError
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.SequenceLogLevel import SequenceLogLevel
from a_protocol_0.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from a_protocol_0.sequence.SequenceStep import SequenceStep
from a_protocol_0.utils.decorators import p0_subject_slot
from a_protocol_0.utils.utils import get_frame_info, nop


class Sequence(AbstractObject, SequenceStateMachineMixin):
    """ Replacement of the _Framework Task as it does not seem to allow variable timeouts like triggers from listeners.
        Nothing but some pale asyncio imitation. See google doc for details. """
    __subject_events__ = ('terminated',)

    DISABLE_LOGGING = False

    def __init__(self, log_level=SequenceLogLevel.DEBUG, name=None, bypass_errors=False, silent=False, *a, **k):
        super(Sequence, self).__init__(*a, **k)

        self._steps = deque()  # type: Deque[SequenceStep]
        self._current_step = None  # type: Optional[SequenceStep]
        self._res = None
        self._log_level = SequenceLogLevel.DISABLED if (self.DISABLE_LOGGING or silent) else log_level
        self._debug = (self._log_level == SequenceLogLevel.DEBUG)
        self._bypass_errors = bypass_errors
        self._parent_seq = None  # type: Sequence
        # self._debug = debug and not sync
        self._is_condition_seq = False
        if not name:
            frame_info = get_frame_info(2)
            if frame_info:
                name = "%s.%s" % (frame_info.class_name, frame_info.method_name)
        self.name = name

    def __repr__(self):
        return "[seq %s]" % self.name

    def debug_str(self):
        message = "%s in state %s" % (self, self.state)
        if not self._current_step:
            message += " (empty seq)"
        if self._res:
            message += " (res %s)" % self._res

    def __len__(self):
        return len(self._steps)

    @property
    def _parent_seqs(self):
        # type: () -> List[Sequence]
        return [self._parent_seq] + self._parent_seq._parent_seqs if self._parent_seq is not None else []

    def _on_start(self):
        self._execute_next_step()

    def _execute_next_step(self):
        if len(self._steps):
            self._current_step = self._steps.popleft()
            if self._debug and self._current_step.debug:
                self.parent.log_info("%s : %s" % (self, self._current_step),
                                     debug=False)
            self._step_termination.subject = self._current_step
            self._current_step.start()
        else:
            self.terminate()

    @p0_subject_slot("terminated")
    def _step_termination(self):
        if (self._current_step.errored or self.song.errored) and not self._bypass_errors:
            self.error()
        elif self._current_step._early_returned:
            self.terminate()
        else:
            self._execute_next_step()

    def _on_terminate(self):
        self._res = self._current_step._res if self._current_step else None

        if self.errored and self._debug:
            self.parent.log_error(self.debug_str, debug=False)

    def add(self, callback=nop, wait=None, name=None, complete_on=None, do_if=None, do_if_not=None, return_if=None,
            return_if_not=None, check_timeout=7, silent=False):
        """
            check_timeout is the number of (exponential duration) checks executed before step failure (based on the Live.Base.Timer tick)
            callback can be :
            - not given (nop): can be used to just wait on a condition
            - a callable or a list of callable (parallel sequence execution) which are added as SequenceStep
        """
        assert callback
        assert not self.terminated or self.errored

        # common error
        if isinstance(callback, Sequence):
            raise SequenceError(object=self,
                                message="You passed a Sequence object instead of a Sequence factory to add")

        self._steps.append(
            SequenceStep.make(self, callback, wait=wait, name=name, complete_on=complete_on, do_if=do_if,
                              do_if_not=do_if_not,
                              return_if=return_if, return_if_not=return_if_not, check_timeout=check_timeout,
                              silent=silent))

        return self

    def done(self):
        # type: () -> Sequence
        self.start()
        return self

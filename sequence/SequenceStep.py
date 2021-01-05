from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.sequence.SequenceError import SequenceError
from a_protocol_0.sequence.SequenceState import SequenceState
from a_protocol_0.utils.decorators import timeout_limit
from a_protocol_0.utils.utils import _has_callback_queue, is_lambda, get_callable_name

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.sequence.Sequence import Sequence


class SequenceStep(AbstractControlSurfaceComponent):
    def __init__(self, func, sequence, wait=None, name=None, complete_on=None,
                 do_if=None, do_if_not=None, return_if=None, return_if_not=None, *a, **k):
        # type: (callable, Sequence, float, str, callable, bool) -> None
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__(*a, **k)
        self._seq = sequence
        self._debug = sequence._debug
        self._callable = func
        self.name = "step %s" % (name or get_callable_name(func))
        self._wait = wait if wait is not None else sequence._wait
        self._state = SequenceState.UN_STARTED
        self._complete_on = complete_on
        self._check_timeout = 5  # around 3.1 s
        self._check_count = 0
        self._res = None
        self._errored = False
        self._by_passed_seq = False
        self._is_terminal_step = False
        self._do_if = do_if
        self._do_if_not = do_if_not
        self._if_condition = None
        self._return_if = return_if
        self._return_if_not = return_if_not
        self._return_condition = None

        conditions = [do_if, do_if_not, return_if, return_if_not]
        if len(filter(None, conditions)) > 1:
            raise SequenceError(sequence=self._seq, message="You cannot specify multiple conditions in a step")
        from a_protocol_0.sequence.Sequence import Sequence
        if any([isinstance(condition, Sequence) for condition in conditions]):
            raise SequenceError(sequence=self._seq,
                                message="You passed a Sequence object instead of a function returning a Sequence for a condition")

    def __repr__(self):
        output = self.name
        if self._wait:
            output += " (and wait %s)" % self._wait
        if self._complete_on:
            if _has_callback_queue(self._complete_on):
                output += " (and wait for listener call : %s)" % get_callable_name(self._complete_on)
            elif is_lambda(self._complete_on):
                output += " (and poll for lambda condition)"
            else:
                output += " (and poll for %s)" % get_callable_name(self._complete_on)
        if self._do_if or self._do_if_not:
            output += " (has if condition)"
        if self._return_if or self._return_if_not:
            output += " (has return condition)"

        return output

    def __call__(self):
        if self._state != SequenceState.UN_STARTED:
            raise SequenceError(sequence=self._seq, message="You cannot start a step twice")

        self._state = SequenceState.STARTED

        from a_protocol_0.sequence.Sequence import Sequence
        if self._do_if or self._do_if_not:
            if_res = self._if_condition()
            if isinstance(if_res, Sequence):
                if_res._is_condition_seq = True
                if self._if_condition._state == SequenceState.TERMINATED:
                    self._terminate_if_condition()
                else:
                    self._terminate_if_condition.subject = self._if_condition
        elif self._return_if or self._return_if_not:
            return_res = self._return_condition()
            if isinstance(return_res, Sequence):
                return_res._is_condition_seq = True
                if self._if_condition._state == SequenceState.TERMINATED:
                    self._terminate_return_condition()
                else:
                    self._terminate_return_condition.subject = self._return_condition
        else:
            self._execute()

    @subject_slot("terminated")
    def _terminate_if_condition(self, res=None):
        if_res = res or self._if_condition._res
        self.parent.log_debug("%s returned %s" % (self, if_res))

        if (if_res and self._do_if) or (not if_res and self._do_if_not):
            self._execute()
        else:
            self._res = True
            self._terminate()

    @subject_slot("terminated")
    def _terminate_return_condition(self):
        return_res = self._return_condition._res
        self.parent.log_debug("%s returned %s" % (self, return_res))

        if (return_res and self._return_if) or (not return_res and self._return_if_not):
            self._terminate(early_return_seq=True)
        else:
            self._execute()

    def _check_for_step_completion(self):
        if not self._complete_on:
            if self._wait:
                self.parent._wait(self._wait, self._terminate)
            else:
                self._terminate()
            return

        if self._check_count == self._check_timeout:
            self._step_timed_out()
            return

        elif _has_callback_queue(self._complete_on):
            self._complete_on._callbacks.append(
                timeout_limit(self._terminate, timeout_limit=pow(2, self._check_timeout),
                              on_timeout=self._step_timed_out))
            return
        elif not self._complete_on():
            self.parent._wait(pow(2, self._check_count), self._check_for_step_completion)
            self._check_count += 1
            return

        self._terminate()

    def _execute(self):
        res = self._callable()
        from a_protocol_0.sequence.Sequence import Sequence
        if isinstance(res, Sequence):
            res._parent_seq = self._seq
            if res._state == SequenceState.TERMINATED:
                raise SequenceError(sequence=self._seq, message="The inner sequence %s was terminated before execution" % res)
            self._step_sequence_terminated_listener.subject = res
            res()
        else:
            self._res = res
            self._check_for_step_completion()

    def _step_timed_out(self):
        self.parent.log_error("timeout error on sequence step waiting for completion %s" % self._complete_on,
                              debug=False)
        self._res = False
        self._terminate()

    @subject_slot("terminated")
    def _step_sequence_terminated_listener(self):
        self._res = self._step_sequence_terminated_listener.subject._res
        self._check_for_step_completion()

    def _terminate(self, early_return_seq=False):
        self._state = SequenceState.TERMINATED

        if self._res is False:
            self._errored = True

        if early_return_seq:
            self._seq._early_returned = True

        if early_return_seq or self._errored:
            self._seq._terminate()
        else:
            self._seq._exec_next()

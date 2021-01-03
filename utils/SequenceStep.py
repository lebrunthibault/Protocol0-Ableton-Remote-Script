from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.decorators import timeout_limit
from a_protocol_0.utils.utils import _has_callback_queue, is_lambda, get_callable_name

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.utils.Sequence import Sequence

UN_STARTED = 0
STARTED = 1
TERMINATED = 2
ERRORED = 3


class SequenceStep(AbstractControlSurfaceComponent):
    def __init__(self, func, sequence, wait=None, name=None, complete_on=None, do_if=None, do_if_not=None, return_if=None, return_if_not=None, *a, **k):
        # type: (callable, Sequence, float, str, callable, bool) -> None
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__(*a, **k)
        self._seq = sequence
        self._debug = sequence._debug
        self._callable = func
        self.name = name or get_callable_name(func)
        self._wait = wait if wait is not None else sequence._wait
        self._state = UN_STARTED
        self._complete_on = complete_on
        self._check_timeout = 5  # around 3.1 s
        self._check_count = 0
        self._res = None
        self._if_condition = None
        self._return_condition = None

        # conditional execution
        from a_protocol_0.utils.Sequence import Sequence
        self._do_if = do_if
        self._do_if_not = do_if_not
        if do_if and do_if_not:
            raise RuntimeError("You cannot specify both do_if and do_if_not in SequenceStep")
        if do_if or do_if_not:
            self._if_condition = Sequence("if_condition").add(do_if or do_if_not)
            self._handle_if_condition.subject = self._if_condition

        # conditional sequence return
        self._return_if = return_if
        self._return_if_not = return_if_not
        if return_if and return_if_not:
            raise RuntimeError("You cannot specify both return_if and return_if_not in SequenceStep")
        if return_if or return_if_not:
            self._return_condition = Sequence("return_condition").add(return_if or return_if_not)
            self._handle_return_condition.subject = self._return_condition

        if self._if_condition and self._return_condition:
            raise RuntimeError("You cannot specify both an if condition and a return condition in a SequenceStep")

        if not callable(func):
            raise RuntimeError("You passed a non callable to a sequence : %s to %s" % (func, self))

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
        if self._state != UN_STARTED:
            return

        self._state = STARTED

        if self._if_condition:
            self._if_condition()
        elif self._return_condition:
            self._return_condition()
        else:
            self._execute()

    @subject_slot("terminated")
    def _handle_if_condition(self):
        if_res = self._if_condition._res
        self.parent.log_debug("_if_condition returned %s" % if_res)

        if (if_res and self._do_if) or (not if_res and self._do_if_not):
            self._execute()
        else:
            self._res = True
            self._terminate()

    @subject_slot("terminated")
    def _handle_return_condition(self):
        return_res = self._return_condition._res
        self.parent.log_debug("_return_condition returned %s" % return_res)

        if (return_res and self._return_if) or (not return_res and self._return_if_not):
            self._terminate(stop_seq=True)
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

    def _handle_sequence_step(self, seq, call=False):
        # type: (Sequence) -> None
        if call:
            seq()
        if seq._state == TERMINATED:
            self._res = seq._res
            self._check_for_step_completion()
        else:
            self._step_sequence_terminated_listener.subject = seq
        return

    def _execute(self):
        res = self._callable()
        from a_protocol_0.utils.Sequence import Sequence
        if isinstance(self._callable, Sequence):
            return self._handle_sequence_step(seq=self._callable)

        if isinstance(res, Sequence):
            if not is_lambda(self._callable):
                # this must be an error
                raise RuntimeError("Wrong usage of sequence, sequence should be generated synchronously (%s) on %s" % (
                    self, self._seq))
            else:
                return self._handle_sequence_step(seq=res, call=True)

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

    def _terminate(self, stop_seq=False):
        self._state = TERMINATED

        if self._res is False:
            self._state = ERRORED

        if stop_seq:
            self._by_passed_seq = True

        if stop_seq or self._state == ERRORED:
            self._seq._terminate()
        else:
            self._seq._exec_next()

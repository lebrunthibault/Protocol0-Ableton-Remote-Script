from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.errors.SequenceError import SequenceError
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.SequenceState import SequenceState, SequenceLogLevel
from a_protocol_0.utils.timeout import TimeoutLimit
from a_protocol_0.utils.utils import _has_callback_queue, is_lambda, get_callable_name, nop

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.sequence.Sequence import Sequence


class SequenceStep(AbstractObject):
    __subject_events__ = ('terminated',)

    def __init__(self, func, sequence, wait, name, complete_on,
                 do_if, do_if_not, return_if, return_if_not, check_timeout, silent, log_level, *a, **k):
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__(*a, **k)
        self._seq = sequence  # type: Sequence
        self._log_level = log_level
        self._debug = log_level == SequenceLogLevel.debug
        self._callable = func

        if not callable(self._callable):
            raise SequenceError(object=self,
                                message="You passed a non callable to a SequenceStep : %s to %s, type: %s" % (
                                    self._callable, self, type(self._callable)))

        self._original_name = name
        if not name and func == nop:
            name = ("wait %s" % wait if wait else "pass")
        self.name = "step %s" % (name or get_callable_name(func))
        self._wait = wait if wait is not None else sequence._wait
        self._state = SequenceState.UN_STARTED
        self._complete_on = complete_on
        self._check_timeout = check_timeout
        self._check_count = 0
        self._callback_timeout = None  # type: callable
        self._res = None
        self._silent = silent
        self._errored = False
        self._by_passed_seq = False
        self._is_terminal_step = False
        self._do_if = do_if
        self._do_if_not = do_if_not
        self._if_condition = None
        self._return_if = return_if
        self._return_if_not = return_if_not
        self._return_condition = None
        self._early_returned = False

        conditions = [do_if, do_if_not, return_if, return_if_not]
        self._condition = next((c for c in conditions if c), None)

        if len(filter(None, conditions)) > 1:
            raise SequenceError(object=self, message="You cannot specify multiple conditions in a step")
        from a_protocol_0.sequence.Sequence import Sequence
        if any([isinstance(condition, Sequence) for condition in conditions]):
            raise SequenceError(object=self,
                                message="You passed a Sequence object instead of a function returning a Sequence for a condition")

    def __repr__(self):
        output = self.name
        if self._complete_on:
            if _has_callback_queue(self._complete_on):
                output += " (and wait for listener call : %s)" % get_callable_name(self._complete_on)
            elif is_lambda(self._complete_on) and not self._original_name and self._debug:
                output += " (and poll for lambda condition)"
            else:
                output += " (and poll for %s)" % get_callable_name(self._complete_on)
        if self._do_if:
            output += " (has_if)"
        elif self._do_if_not:
            output += " (has_if_not)"
        elif self._return_if:
            output += " (has_return_if)"
        elif self._return_if_not:
            output += " (has_return_if_not)"

        return "[%s]" % output

    def _start(self):
        if self._state != SequenceState.UN_STARTED:
            raise SequenceError(object=self, message="You cannot start a step twice")

        self._state = SequenceState.STARTED

        if self._condition:
            self._create_condition_check()
        else:
            self._execute()

    def _create_condition_check(self):
        terminate = self._terminate_if_condition if self._condition in [self._do_if,
                                                                        self._do_if_not] else self._terminate_return_condition

        condition_res = self._execute_callable(self._condition)
        if self._errored:
            return  # error on condition

        from a_protocol_0.sequence.Sequence import Sequence
        if isinstance(condition_res, Sequence):
            condition_res._is_condition_seq = True
            terminate.subject = condition_res
            condition_res._start()
        else:
            terminate(res=condition_res)

    @subject_slot("terminated")
    def _terminate_if_condition(self, res=None):
        if_res = res
        if if_res is not None and self._terminate_if_condition.subject:
            if_res = self._terminate_if_condition.subject._res
        if self._debug:
            self.parent.log_info("%s condition returned %s" % (self, if_res))

        if (if_res and self._do_if) or (not if_res and self._do_if_not):
            self._execute()
        else:
            self._res = True  # Sequence is not an error
            self._terminate()

    @subject_slot("terminated")
    def _terminate_return_condition(self, res=None):
        return_res = res
        if return_res is not None and self._terminate_return_condition.subject:
            return_res = self._terminate_return_condition.subject._res
        if self._debug:
            self.parent.log_info("%s condition returned %s" % (self, return_res))

        if (return_res and self._return_if) or (not return_res and self._return_if_not):
            self._early_returned = True
            self._terminate()
        else:
            self._execute()

    def _check_for_step_completion(self):
        if not self._complete_on:
            if self._wait:
                self.parent.log_dev(self._wait)
                self.parent._wait(self._wait, self._terminate)
            else:
                self._terminate()
            return

        if _has_callback_queue(self._complete_on):
            return self._add_callback_on_listener(self._complete_on)
        else:
            check_res = self._execute_callable(self._complete_on)
            if self._errored:
                return

            if _has_callback_queue(check_res):  # allows async linking to a listener
                return self._add_callback_on_listener(check_res)

            if check_res or self._check_timeout == 0:
                self._terminate()
            else:
                if self._check_count == self._check_timeout:
                    self._step_timed_out()
                    return
                self.parent._wait(10 * pow(3, self._check_count), self._check_for_step_completion)
                self._check_count += 1

    def _add_callback_on_listener(self, listener):
        if not self._check_timeout:
            listener.add_callback(self._terminate)
        else:
            self._callback_timeout = TimeoutLimit(func=self._terminate, awaited_listener=listener,
                                                  timeout_limit=self._check_timeout * 100,
                                                  on_timeout=self._step_timed_out)
            listener.add_callback(self._callback_timeout)

    def _execute_callable(self, func):
        try:
            return func()
        except (Exception, RuntimeError) as e:
            if self._log_level >= SequenceLogLevel.info and not self._silent:
                self.parent.log_error("Error in _execute callable for step %s" % self)
            self._errored = True
            # here we could check for Changes cannot be triggered by notifications and retry.
            # But if the function has side effects before raising the exception that will not work
            # We could in this case check that the function or method is not user code and in this case retry
            self._terminate()

    def _execute(self):
        res = self._execute_callable(self._callable)
        if self._errored:
            return

        from a_protocol_0.sequence.Sequence import Sequence
        if isinstance(res, Sequence) and res._state != SequenceState.TERMINATED:
            res._parent_seq = self._seq
            self._step_sequence_terminated_listener.subject = res
            res._start()
        else:
            self._res = res
            self._check_for_step_completion()

    def _step_timed_out(self):
        if _has_callback_queue(self._complete_on) and self._callback_timeout:
            self._complete_on.remove_callback(self._callback_timeout)

        if self._log_level >= SequenceLogLevel.info:
            self.parent.log_error("timeout completion error on %s %s" % (self, self._seq), debug=False)

        self._errored = True
        self._terminate()

    @subject_slot("terminated")
    def _step_sequence_terminated_listener(self):
        self._res = self._step_sequence_terminated_listener.subject._res
        self._check_for_step_completion()

    def _terminate(self):
        if self._state == SequenceState.TERMINATED:
            raise SequenceError("You called terminate twice on %s" % self)

        self._state = SequenceState.TERMINATED

        # noinspection PyUnresolvedReferences
        self.notify_terminated()

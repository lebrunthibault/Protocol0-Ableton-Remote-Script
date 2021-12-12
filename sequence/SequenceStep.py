from functools import partial

from typing import TYPE_CHECKING, Iterable, Any, Union, Callable, Optional, cast, List

from protocol0.config import Config
from protocol0.errors.SequenceError import SequenceError
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.utils.callback_descriptor import CallableWithCallbacks
from protocol0.utils.decorators import p0_subject_slot
from protocol0.utils.timeout import TimeoutLimit
from protocol0.utils.utils import _has_callback_queue, is_lambda, get_callable_repr, nop

if TYPE_CHECKING:
    from protocol0.sequence.Sequence import Sequence


class SequenceStep(AbstractObject, SequenceStateMachineMixin):
    __subject_events__ = ("terminated", "errored")

    def __init__(
            self,
            func,  # type: Callable
            sequence,  # type: Sequence
            name,  # type: str
            wait,  # type: int
            wait_beats,  # type: int
            wait_for_system,  # type: bool
            no_cancel,  # type: bool
            no_wait,  # type: bool
            complete_on,  # type: Optional[Union[Callable, CallableWithCallbacks]]
            do_if,  # type: Optional[Callable]
            check_timeout,  # type: int
            silent,  # type: bool
            *a,  # type: Any
            **k  # type: Any
    ):
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__(*a, **k)
        self.debug = False if silent else sequence.debug
        self._original_name = name
        if not name and func == nop:
            name = "wait %s" % wait if wait else "pass"
        self.name = "step %s" % (name or get_callable_repr(func))
        self._sequence_name = sequence.name
        self._callable = func
        self._wait = wait or 0
        self._wait_beats = wait_beats or 0
        self._no_wait = no_wait
        self.wait_for_system = wait_for_system
        self.no_cancel = no_cancel
        self._complete_on = complete_on
        self._check_timeout = check_timeout
        self._check_count = 0
        self._callback_timeout = None  # type: Optional[Callable]
        self.res = None  # type: Optional[Any]
        self._do_if = do_if
        self._condition = do_if

        if self.wait_for_system:
            assert self._wait == 0 and self._wait_beats == 0 and self._complete_on is None, "waiting for system excludes other waiting options"
        if self._complete_on:
            assert self._wait == 0 and self._wait_beats == 0, "complete_on excludes wait and wait_beats"
        if self._wait:
            assert self._wait_beats == 0, "wait excludes wait_beats"
        if self.no_cancel:
            assert self.wait_for_system, "no cancel used without wait_for_system"
        assert callable(self._callable), "You passed a non callable (%s) to %s" % (self._callable, self)
        from protocol0.sequence.Sequence import Sequence

        assert not isinstance(self._condition,
                              Sequence), "You passed a Sequence object instead of a Sequence factory for a condition"

        if Config.SEQUENCE_SLOW_MO:
            self._wait = min(100, self._wait * 5)
            self._check_timeout *= 5

    def __repr__(self):
        # type: () -> str
        output = self.name
        if self.wait_for_system:
            output += " (and wait for system)"
        if self.no_cancel:
            output += " - no cancel"
        elif self._complete_on:
            if _has_callback_queue(self._complete_on):
                output += " (and wait for listener call : %s)" % get_callable_repr(self._complete_on)
            elif is_lambda(self._complete_on) and not self._original_name and self.debug:
                output += " (and poll for lambda condition)"
            else:
                output += " (and poll for %s)" % get_callable_repr(self._complete_on)
        elif self._wait_beats:
            output += " (and wait_beats %s)" % self._wait_beats
        elif self._wait_beats:
            output += " (no wait)"
        if self._do_if:
            output += " (has_if)"

        return "[%s]" % output

    @staticmethod
    def make(sequence, callback, *a, **k):
        # type: (Sequence, Union[Callable, Iterable], Any, Any) -> SequenceStep
        if isinstance(callback, Iterable):
            def parallel_sequence_creator(callbacks):
                # type: (List[Callable]) -> Sequence
                from protocol0.sequence.ParallelSequence import ParallelSequence

                seq = ParallelSequence(silent=not sequence.debug)
                [seq.add(func) for func in callbacks]
                return seq.done()

            callback = partial(parallel_sequence_creator, callback)

        return SequenceStep(callback, sequence=sequence, *a, **k)

    def _on_start(self):
        # type: () -> None
        if self._condition:
            self._execute_condition()
        else:
            self._execute()

    def _execute_condition(self):
        # type: () -> None
        terminate_callback = cast(
            CallableWithCallbacks,
            (self._terminate_if_condition if self._condition == self._do_if else self._terminate_return_condition),
        )
        try:
            condition_res = self._execute_callable(cast(Callable, self._condition))
        except SequenceError:
            return

        self._handle_return_value(condition_res, terminate_callback, terminate_callback)

    @p0_subject_slot("terminated")
    def _terminate_if_condition(self, res=None):
        # type: (Optional[Any]) -> None
        if_res = res
        if if_res is not None and self._terminate_if_condition.subject:
            if_res = self._terminate_if_condition.subject.res
        if self.debug:
            self.parent.log_info("%s condition returned %s" % (self, if_res))

        if if_res and self._do_if:
            self._execute()
        else:
            self.res = True  # Sequence is not an error
            self.terminate()

    @p0_subject_slot("terminated")
    def _terminate_return_condition(self, res=None):
        # type: (Optional[Any]) -> None
        return_res = res
        if return_res is not None and self._terminate_return_condition.subject:
            return_res = self._terminate_return_condition.subject.res
        if self.debug:
            self.parent.log_info("%s condition returned %s" % (self, return_res))

        self._execute()

    def _check_for_step_completion(self, _=None):
        # type: (Any) -> None
        if not self._complete_on and not self._wait and not self._wait_beats:
            self.terminate()
            return

        if self._wait:
            self.parent.wait(self._wait, self.terminate)
            return

        if self._wait_beats:
            self.parent.wait_beats(self._wait_beats, self.terminate)
            return

        # we have complete_on
        if _has_callback_queue(self._complete_on):
            self._add_callback_on_listener(cast(CallableWithCallbacks, self._complete_on))
            return

        try:
            check_res = self._execute_callable(cast(Callable, self._complete_on))
        except SequenceError:
            return  # handled

        if _has_callback_queue(check_res):  # allows async linking to a listener
            return self._add_callback_on_listener(cast(CallableWithCallbacks, check_res))

        if check_res:
            self.terminate()
        else:
            self._exponential_check()

    def _exponential_check(self):
        # type: () -> None
        if self._check_count == self._check_timeout:
            self._step_timed_out()
            return
        self.parent.wait(pow(2, self._check_count), self._check_for_step_completion)
        self._check_count += 1

    def _add_callback_on_listener(self, listener):
        # type: (CallableWithCallbacks) -> None
        if not self._check_timeout:
            listener.add_callback(self.terminate)
        else:
            self._callback_timeout = TimeoutLimit(
                func=self.terminate,
                awaited_listener=listener,
                timeout_limit=self._check_timeout,
                on_timeout=self._step_timed_out,
            )
            listener.add_callback(self._callback_timeout)

    def _execute_callable(self, func):
        # type: (Callable) -> Any
        try:
            return func()
        except SequenceError as e:
            self.parent.log_error("caught sequence error: %s" % e)
            raise
        except Exception:
            self.error()
            self.parent.errorManager.handle_error("%s : %s" % (self._sequence_name, self))
            raise SequenceError()  # will stop sequence processing

    def _handle_return_value(self, res, listener, success_callback):
        # type: (Any, CallableWithCallbacks, Callable) -> None
        from protocol0.sequence.Sequence import Sequence

        if isinstance(res, Sequence) and self._no_wait is False:
            if res.errored:
                self.error()
            elif res.terminated:
                success_callback(res.res)
            else:
                listener.subject = res  # type: ignore[attr-defined]
                if not res.started:
                    res.start()
        else:
            success_callback(res)

    def _execute(self):
        # type: () -> None
        try:
            res = self._execute_callable(self._callable)
        except SequenceError:
            return

        self._handle_return_value(res, self._step_sequence_terminated_listener,  # type: ignore[arg-type]
                                  self._check_for_step_completion)

    def _step_timed_out(self):
        # type: () -> None
        if isinstance(self._complete_on, CallableWithCallbacks) and self._callback_timeout:
            self._complete_on.clear_callbacks()

        if self.debug:
            self.parent.log_error("timeout completion error on %s" % self, debug=False)

        self.error()

    @p0_subject_slot("terminated")
    def _step_sequence_terminated_listener(self):
        # type: () -> None
        self.res = self._step_sequence_terminated_listener.subject.res
        self._check_for_step_completion()

from functools import partial

from typing import TYPE_CHECKING, Iterable, Any, Union, Callable, Optional, cast, List

from protocol0.application.config import Config
from protocol0.application.service.decorators import handle_error
from protocol0.domain.sequence.CallbackDescriptor import CallableWithCallbacks
from protocol0.domain.sequence.SequenceError import SequenceError
from protocol0.domain.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.domain.sequence.TimeoutLimit import TimeoutLimit
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.utils import _has_callback_queue, get_callable_repr, nop
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.shared.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.sequence.Sequence import Sequence


class SequenceStep(SequenceStateMachineMixin):
    def __init__(
            self,
            func,  # type: Callable
            sequence,  # type: Sequence
            name,  # type: str
            wait,  # type: int
            wait_beats,  # type: float
            wait_for_system,  # type: bool
            no_cancel,  # type: bool
            complete_on,  # type: Optional[Union[Callable, CallableWithCallbacks]]
            check_timeout,  # type: int
            *a,  # type: Any
            **k  # type: Any
    ):
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__(*a, **k)
        if not name and func == nop:
            name = "wait %s" % wait if wait else "pass"
        self.name = "step %s" % (name or get_callable_repr(func))
        self._sequence_name = sequence.name
        self._callable = func
        self._wait = wait
        self._wait_beats = wait_beats or 0
        self.wait_for_system = wait_for_system
        self.no_cancel = no_cancel
        self._complete_on = complete_on
        self._check_timeout = check_timeout
        self._callback_timeout = None  # type: Optional[Callable]
        self.res = None  # type: Optional[Any]

        if self.wait_for_system:
            assert self._wait == 0 and self._wait_beats == 0 and self._complete_on is None, "waiting for system excludes other waiting options"
        if self._complete_on:
            assert self._wait == 0 and self._wait_beats == 0, "complete_on excludes wait and wait_beats"
        if self._wait:
            assert self._wait_beats == 0, "wait excludes wait_beats"
        if self.no_cancel:
            assert self.wait_for_system, "no cancel used without wait_for_system"
        assert callable(self._callable), "You passed a non callable (%s) to %s" % (self._callable, self)
        from protocol0.domain.sequence.Sequence import Sequence

        if Config.SEQUENCE_SLOW_MO:
            self._wait = min(100, self._wait * 5)
            self._check_timeout += 5

    def __repr__(self, **k):
        # type: (Any) -> str
        output = self.name
        if self.wait_for_system:
            output += " (and wait for system)"
        elif self._complete_on:
            output += " (and wait for listener call : %s)" % get_callable_repr(self._complete_on)
        elif self._wait:
            output += " (and wait %s)" % self._wait
        elif self._wait_beats:
            output += " (and wait_beats %.2f)" % self._wait_beats

        return "[%s]" % output

    @staticmethod
    def make(sequence, callback, *a, **k):
        # type: (Sequence, Union[Callable, Iterable], Any, Any) -> SequenceStep
        if isinstance(callback, Iterable):
            def parallel_sequence_creator(callbacks):
                # type: (List[Callable]) -> Sequence
                from protocol0.domain.sequence.ParallelSequence import ParallelSequence

                seq = ParallelSequence()
                [seq.add(func) for func in callbacks]
                return seq.done()

            callback = partial(parallel_sequence_creator, callback)

        return SequenceStep(callback, sequence=sequence, *a, **k)

    def _on_start(self):
        # type: () -> None
        try:
            self._execute()
        except SequenceError as e:
            self.error(e.message)

    def _check_for_step_completion(self, _=None):
        # type: (Any) -> None
        if not self._complete_on and not self._wait and not self._wait_beats:
            self.terminate()
            return

        if self._wait:
            Scheduler.wait(self._wait, self.terminate)
            return

        if self._wait_beats:
            BeatScheduler.get_instance().wait_beats(self._wait_beats, self.terminate)
            return

        # we have complete_on there
        self._handle_complete_on()

    def _handle_complete_on(self):
        # type: () -> None
        # complete_on is a listener
        if _has_callback_queue(self._complete_on):
            self._postpone_termination_after_listener(cast(CallableWithCallbacks, self._complete_on))
            return

        try:
            callable_response = self._execute_callable(cast(Callable, self._complete_on))
        except SequenceError:
            return  # handled

        # complete on is a listener computed at step execution (that is lambda: <listener>)
        if _has_callback_queue(callable_response):  # allows async linking to a listener
            return self._postpone_termination_after_listener(cast(CallableWithCallbacks, callable_response))
        else:
            raise SequenceError("on complete_on should have a callback queue")

    def _postpone_termination_after_listener(self, listener):
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

    @handle_error
    def _execute_callable(self, func):
        # type: (Callable) -> Any
        try:
            return func()
        except SequenceError:
            raise
        except Exception:
            self.error()
            from protocol0 import Protocol0
            Protocol0.SELF.errorManager.handle_error("%s : %s" % (self._sequence_name, self))
            raise SequenceError()  # will stop sequence processing

    def _execute(self):
        # type: () -> None
        res = self._execute_callable(self._callable)

        from protocol0.domain.sequence.Sequence import Sequence

        if isinstance(res, Sequence):
            if res.errored:
                self.error()
            elif res.cancelled:
                self.cancel()
            elif res.terminated:
                self._check_for_step_completion(res.res)
            else:
                self._step_sequence_terminated_listener.subject = res  # type: ignore[attr-defined]
                if not res.started:
                    res.start()
        else:
            self._check_for_step_completion(res)

    def _step_timed_out(self):
        # type: () -> None
        if isinstance(self._complete_on, CallableWithCallbacks) and self._callback_timeout:
            self._complete_on.clear_callbacks()

        Logger.log_warning("timeout completion error on %s" % self, debug=False)

        self.error()

    @p0_subject_slot("terminated")
    def _step_sequence_terminated_listener(self):
        # type: () -> None
        self.res = self._step_sequence_terminated_listener.subject.res
        try:
            self._check_for_step_completion()
        except SequenceError as e:
            self.error(e.message)

from functools import partial

from typing import TYPE_CHECKING, Iterable, Any, Union, Callable, Optional, cast, List

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import get_callable_repr
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.CallbackDescriptor import CallableWithCallbacks
from protocol0.shared.sequence.SequenceError import SequenceError
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin
from protocol0.shared.sequence.TimeoutLimit import TimeoutLimit

if TYPE_CHECKING:
    from protocol0.shared.sequence.Sequence import Sequence


def _has_callback_queue(func):
    # type: (Any) -> bool
    """ mixing duck typing and isinstance to ensure we really have a callback handler object """
    from protocol0.shared.sequence.CallbackDescriptor import CallableWithCallbacks
    from _Framework.SubjectSlot import CallableSlotMixin

    return (
            func
            and hasattr(func, "add_callback")
            and (isinstance(func, CallableWithCallbacks) or isinstance(func, CallableSlotMixin))
    )


class SequenceStep(UseFrameworkEvents, SequenceStateMachineMixin):
    __subject_events__ = ("terminated", "errored", "cancelled")

    def __init__(
            self,
            func,  # type: Callable
            sequence,  # type: Sequence
            name,  # type: str
            wait_for_system,  # type: bool
            no_cancel,  # type: bool
            complete_on,  # type: Optional[Union[Callable, CallableWithCallbacks]]
            check_timeout,  # type: int
            no_terminate,  # type: bool
    ):
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__()
        self.name = "step %s" % (name or get_callable_repr(func))
        self._sequence_name = sequence.name
        self._callable = func
        self.wait_for_system = wait_for_system
        self.no_cancel = no_cancel
        self._complete_on = complete_on
        self._check_timeout = check_timeout
        self._callback_timeout = None  # type: Optional[Callable]
        self._no_terminate = no_terminate
        self.res = None  # type: Optional[Any]

        waiting_conditions = iter(
            [self.wait_for_system, self._complete_on])
        if any(waiting_conditions) and any(waiting_conditions):
            raise Protocol0Error("Found multiple concurrent waiting conditions in %s" % self)
        if self.no_cancel:
            assert self.wait_for_system, "no cancel used without wait_for_system"
        assert callable(self._callable), "You passed a non callable (%s) to %s" % (self._callable, self)
        from protocol0.shared.sequence.Sequence import Sequence

    def __repr__(self, **k):
        # type: (Any) -> str
        output = self.name
        if self.wait_for_system:
            output += " (and wait for system)"
        elif self._complete_on:
            output += " (and wait for listener call : %s)" % get_callable_repr(self._complete_on)

        return "[%s]" % output

    @classmethod
    def make(cls, sequence, callback, *a, **k):
        # type: (Sequence, Union[Callable, Iterable], Any, Any) -> SequenceStep
        if isinstance(callback, List):
            def parallel_sequence_creator(callbacks):
                # type: (List[Callable]) -> Sequence
                from protocol0.shared.sequence.ParallelSequence import ParallelSequence

                seq = ParallelSequence()
                [seq.add(func) for func in callbacks]
                return seq.done()

            callback = partial(parallel_sequence_creator, callback)

        return SequenceStep(callback, sequence=sequence, *a, **k)

    def start(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.STARTED)
        try:
            self._execute()
        except SequenceError as e:
            if not self.errored:
                self._error(e.message)

    def _check_for_step_completion(self, res=None):
        # type: (Any) -> None
        self.res = res

        if self._complete_on:
            self._handle_complete_on()
            return

        self._terminate()

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
            listener.add_callback(self._terminate)
        else:
            self._callback_timeout = TimeoutLimit(
                func=self._terminate,
                awaited_listener=listener,
                timeout_limit=self._check_timeout,
                on_timeout=self._step_timed_out,
            )
            listener.add_callback(self._callback_timeout)

    def _execute_callable(self, func):
        # type: (Callable) -> Any
        try:
            return func()
        except SequenceError:
            raise
        except Exception:
            self._error()
            DomainEventBus.notify(ErrorRaisedEvent("%s : %s" % (self._sequence_name, self)))
            raise SequenceError()  # will stop sequence processing

    def _execute(self):
        # type: () -> None
        res = self._execute_callable(self._callable)

        from protocol0.shared.sequence.Sequence import Sequence

        if isinstance(res, Sequence):
            if res.errored:
                self._error()
            elif res.cancelled:
                self.cancel()
            elif res.terminated:
                self._check_for_step_completion(res.res)
            else:
                self._sequence_terminated_listener.subject = res  # type: ignore[attr-defined]
                if not res.started:
                    res.start()
        else:
            self._check_for_step_completion(res)

    def _step_timed_out(self):
        # type: () -> None
        if isinstance(self._complete_on, CallableWithCallbacks) and self._callback_timeout:
            self._complete_on.clear_callbacks()

        Logger.log_warning("timeout completion error on %s" % self)

        self._error()

    @p0_subject_slot("terminated")
    def _sequence_terminated_listener(self):
        # type: () -> None
        self.res = self._sequence_terminated_listener.subject.res
        try:
            self._check_for_step_completion()
        except SequenceError as e:
            self._error(e.message)

    def _error(self, message=None):
        # type: (Optional[str]) -> None
        if self.cancelled:
            return
        if message:
            Logger.log_error(message)
        self.change_state(SequenceStateEnum.ERRORED)
        self.notify_errored()  # type: ignore[attr-defined]
        self.disconnect()

    def cancel(self, notify=True):
        # type: (bool) -> None
        if self.errored:
            return
        self.change_state(SequenceStateEnum.CANCELLED)
        if notify:
            self.notify_cancelled()  # type: ignore[attr-defined]
        self.disconnect()

    def _terminate(self):
        # type: () -> None
        if self.cancelled or self.errored:
            return
        self.change_state(SequenceStateEnum.TERMINATED)
        if not self._no_terminate:
            self.notify_terminated()  # type: ignore[attr-defined]
        self.disconnect()

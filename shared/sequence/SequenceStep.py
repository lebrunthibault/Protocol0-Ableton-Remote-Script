from functools import partial

from typing import TYPE_CHECKING, Iterable, Any, Union, Callable, Optional, cast, List, Type

from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import get_callable_repr, nop
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.CallbackDescriptor import CallableWithCallbacks
from protocol0.shared.sequence.SequenceError import SequenceError
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


class SequenceStep(SequenceStateMachineMixin):
    def __init__(
            self,
            func,  # type: Callable
            sequence,  # type: Sequence
            name,  # type: str
            wait,  # type: int
            wait_beats,  # type: float
            wait_for_system,  # type: bool
            wait_for_event,  # type: Type[object]
            no_cancel,  # type: bool
            complete_on,  # type: Optional[Union[Callable, CallableWithCallbacks]]
            check_timeout,  # type: int
    ):
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__()
        if not name and func == nop:
            name = "wait %s" % wait if wait else "pass"
        self.name = "step %s" % (name or get_callable_repr(func))
        self._sequence_name = sequence.name
        self._callable = func
        self._wait = wait
        self._wait_beats = wait_beats or 0
        self.wait_for_system = wait_for_system
        self._wait_for_event = wait_for_event
        self.no_cancel = no_cancel
        self._complete_on = complete_on
        self._check_timeout = check_timeout
        self._callback_timeout = None  # type: Optional[Callable]
        self.res = None  # type: Optional[Any]

        waiting_conditions = iter([self._wait, self._wait_beats, self.wait_for_system, self._wait_for_event, self._complete_on])
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
        if self._wait_for_event:
            output += " (and wait for event %s)" % self._wait_for_event
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
                from protocol0.shared.sequence.ParallelSequence import ParallelSequence

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
            if not self.errored:
                self.error(e.message)

    def _check_for_step_completion(self, res=None):
        # type: (Any) -> None
        self.res = res
        if self._wait:
            Scheduler.wait(self._wait, self.terminate)
            return

        if self._wait_beats:
            Scheduler.wait_beats(self._wait_beats, self.terminate)
            return

        if self._wait_for_event:
            DomainEventBus.subscribe(self._wait_for_event, self._handle_event)
            return

        if self._complete_on:
            self._handle_complete_on()
            return

        self.terminate()

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

    def _handle_event(self, _):
        # type: (object) -> None
        self.terminate()

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

    def _execute_callable(self, func):
        # type: (Callable) -> Any
        try:
            return func()
        except SequenceError:
            raise
        except Exception:
            self.error()
            DomainEventBus.notify(ErrorRaisedEvent("%s : %s" % (self._sequence_name, self)))
            raise SequenceError()  # will stop sequence processing

    def _execute(self):
        # type: () -> None
        res = self._execute_callable(self._callable)

        from protocol0.shared.sequence.Sequence import Sequence

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

        Logger.log_warning("timeout completion error on %s" % self)

        self.error()

    @p0_subject_slot("terminated")
    def _step_sequence_terminated_listener(self):
        # type: () -> None
        self.res = self._step_sequence_terminated_listener.subject.res
        try:
            self._check_for_step_completion()
        except SequenceError as e:
            self.error(e.message)

    def _on_terminate(self):
        # type: () -> None
        if self._wait_for_event:
            DomainEventBus.un_subscribe(self._wait_for_event, self.terminate)

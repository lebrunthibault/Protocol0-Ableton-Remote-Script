from typing import TYPE_CHECKING, Any, Callable, Optional

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.SequenceError import SequenceError
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin

if TYPE_CHECKING:
    from protocol0.shared.sequence.Sequence import Sequence


class SequenceStep(UseFrameworkEvents, SequenceStateMachineMixin):
    __subject_events__ = ("terminated", "errored", "cancelled")

    def __init__(self, func, name, no_timeout, no_terminate):
        # type: (Callable, str, bool, bool) -> None
        """ the tick is 100 ms """
        super(SequenceStep, self).__init__()
        self.name = name
        self._callable = func
        self._no_timeout = no_timeout
        self._callback_timeout = None  # type: Optional[Callable]
        self._no_terminate = no_terminate
        self.res = None  # type: Optional[Any]

    def __repr__(self, **k):
        # type: (Any) -> str
        return self.name

    def start(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.STARTED)
        # noinspection PyBroadException
        try:
            self._execute()
        except Exception:
            self._error()
            DomainEventBus.notify(ErrorRaisedEvent(str(self)))

    def _check_for_step_completion(self, res=None):
        # type: (Any) -> None
        self.res = res
        self._terminate()

    def _execute(self):
        # type: () -> None
        res = self._callable()

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
        else:
            self._check_for_step_completion(res)

    @p0_subject_slot("terminated")
    def _sequence_terminated_listener(self):
        # type: () -> None
        if not self.started:
            return

        self.res = self._sequence_terminated_listener.subject.res
        try:
            self._check_for_step_completion()
        except SequenceError as e:
            self._error(e.message)

    def _error(self, message=None):
        # type: (Optional[str]) -> None
        if self.cancelled or self.errored:
            return
        if message:
            Logger.log_error(message)
        self.change_state(SequenceStateEnum.ERRORED)
        self.notify_errored()  # type: ignore[attr-defined]
        self.disconnect()

    def cancel(self):
        # type: () -> None
        if self.started:
            self.change_state(SequenceStateEnum.CANCELLED)
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

from typing import Any, Callable, Optional

from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.shared.sequence.SequenceState import SequenceStateEnum
from protocol0.shared.sequence.SequenceStateMachineMixin import SequenceStateMachineMixin


class SequenceStep(SequenceStateMachineMixin):
    __subject_events__ = ("terminated", "errored", "cancelled")

    def __init__(self, func, name, notify_terminated):
        # type: (Callable, str, bool) -> None
        super(SequenceStep, self).__init__()
        self._name = name
        self._callable = func
        self._notify_terminated = notify_terminated
        self.res = None  # type: Optional[Any]

    def __repr__(self, **k):
        # type: (Any) -> str
        return self._name

    def start(self):
        # type: () -> None
        self.change_state(SequenceStateEnum.STARTED)
        # noinspection PyBroadException
        try:
            self._execute()
        except Exception:
            self._error()
            DomainEventBus.notify(ErrorRaisedEvent(str(self)))

    def _execute(self):
        # type: () -> None
        res = self._callable()

        if isinstance(res, SequenceStateMachineMixin):
            if res.errored:
                self._error()
            elif res.cancelled:
                self.cancel()
            elif res.terminated:
                self._terminate(res.res)
            else:
                self._sequence_terminated_listener.subject = res  # type: ignore[attr-defined]
        else:
            self._terminate(res)

    @p0_subject_slot("terminated")
    def _sequence_terminated_listener(self):
        # type: () -> None
        self._terminate(self._sequence_terminated_listener.subject.res)

    def _error(self):
        # type: () -> None
        if self.started:
            self.change_state(SequenceStateEnum.ERRORED)
            self.notify_errored()  # type: ignore[attr-defined]
            self.disconnect()

    def cancel(self):
        # type: () -> None
        if self.started:
            self.change_state(SequenceStateEnum.CANCELLED)
            self.notify_cancelled()  # type: ignore[attr-defined]
            self.disconnect()

    def _terminate(self, res):
        # type: (Any) -> None
        if self.cancelled or self.errored:
            return
        self.res = res
        self.change_state(SequenceStateEnum.TERMINATED)
        if self._notify_terminated:
            self.notify_terminated()  # type: ignore[attr-defined]
        self.disconnect()

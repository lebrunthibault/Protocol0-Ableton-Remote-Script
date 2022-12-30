from functools import wraps

from typing import Any

from protocol0.shared.types import Func


def handle_error(func):
    # type: (Func) -> Func
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> Any
        # noinspection PyBroadException
        try:
            return func(*a, **k)
        except Exception:
            from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
            from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent

            DomainEventBus.emit(ErrorRaisedEvent())

    return decorate

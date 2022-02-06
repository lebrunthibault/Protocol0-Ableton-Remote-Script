from functools import wraps

from typing import Any

from protocol0.my_types import Func


def handle_error(func):
    # type: (Func) -> Func
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> Any
        # noinspection PyBroadException
        try:
            return func(*a, **k)
        except Exception:
            from protocol0 import Protocol0

            Protocol0.CONTAINER.error_manager.handle_error()

    return decorate

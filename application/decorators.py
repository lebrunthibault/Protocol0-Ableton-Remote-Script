from functools import wraps

from typing import Any, Callable

from protocol0.my_types import Func


def single_undo(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0

        Protocol0.SELF.protocol0_song.begin_undo_step()
        res = func(*a, **k)
        Protocol0.SELF.protocol0_song.end_undo_step()
        return res

    return decorate


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

            Protocol0.SELF.errorManager.handle_error()

    return decorate

from functools import wraps

from typing import Any, Callable

from protocol0.my_types import Func


def single_undo(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        from protocol0.domain.lom.song.Song import Song

        Song.get_instance().begin_undo_step()
        res = func(*a, **k)
        Song.get_instance().end_undo_step()
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

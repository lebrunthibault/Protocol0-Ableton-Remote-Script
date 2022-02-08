from typing import Any, Callable

from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.utils import get_callable_repr


class SchedulerEvent(object):
    def __init__(self, callback, tick_count):
        # type: (Callable, int) -> None
        self._executed = False
        self._cancelled = False
        self._callback = callback
        self._tick_count = tick_count
        self._ticks_left = tick_count
        self.name = get_callable_repr(self._callback)

    def __repr__(self, **k):
        # type: (Any) -> str
        return "%s (%d / %d)" % (self.name, self._ticks_left, self._tick_count)

    @property
    def is_timeout_elapsed(self):
        # type: () -> bool
        return self._ticks_left == 0

    def decrement_timeout(self):
        # type: () -> None
        assert self._ticks_left > 0
        self._ticks_left -= 1

    def cancel(self):
        # type: () -> None
        self._cancelled = True

    @handle_error
    def execute(self):
        # type: () -> None
        if self._cancelled:
            return

        assert not self._executed
        self._executed = True
        self._callback()

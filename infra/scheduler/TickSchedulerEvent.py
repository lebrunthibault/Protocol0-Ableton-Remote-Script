from typing import Callable

from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)
from protocol0.domain.shared.utils.func import get_callable_repr


class TickSchedulerEvent(TickSchedulerEventInterface):
    def __init__(self, callback, tick_count):
        # type: (Callable, int) -> None
        self.callback = callback
        self._ticks_left = tick_count
        self._cancelled = False

    def __repr__(self):
        # type: () -> str
        return get_callable_repr(self.callback)

    @property
    def should_execute(self):
        # type: () -> bool
        return self._ticks_left == 0

    def decrement_timeout(self):
        # type: () -> None
        assert self._ticks_left > 0, "0 ticks left"
        self._ticks_left -= 1

    def execute(self):
        # type: () -> None
        if not self._cancelled:
            self.callback()

    def cancel(self):
        # type: () -> None
        self._cancelled = True

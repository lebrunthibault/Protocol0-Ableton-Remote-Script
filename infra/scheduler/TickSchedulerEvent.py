from typing import Callable


class TickSchedulerEvent(object):
    def __init__(self, callback, tick_count):
        # type: (Callable, int) -> None
        self._callback = callback
        self._ticks_left = tick_count

    @property
    def should_execute(self):
        # type: () -> bool
        return self._ticks_left == 0

    def decrement_timeout(self):
        # type: () -> None
        assert self._ticks_left > 0
        self._ticks_left -= 1

    def execute(self):
        # type: () -> None
        self._callback()

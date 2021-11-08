from typing import Any, Callable

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.utils.utils import get_callable_repr


class SchedulerEvent(AbstractObject):
    def __init__(self, callback, tick_count, *a, **k):
        # type: (Callable, int, Any, Any) -> None
        super(SchedulerEvent, self).__init__(*a, **k)
        self._executed = False
        self._cancelled = False
        self._callback = callback
        self._tick_count = tick_count
        self._ticks_left = tick_count
        self.name = get_callable_repr(self._callback)

    def __repr__(self):
        # type: () -> str
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

    def execute(self):
        # type: () -> None
        if self._cancelled:
            return

        assert not self._executed
        if self.song.errored:
            return
        self._executed = True
        # noinspection PyBroadException
        try:
            self._callback()
        except Exception:
            self.parent.errorManager.handle_error()

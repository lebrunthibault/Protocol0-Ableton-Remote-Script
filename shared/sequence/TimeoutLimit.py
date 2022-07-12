from typing import Any, Callable

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.func import get_callable_repr
from protocol0.shared.logging.Logger import Logger


class TimeoutLimit(object):
    TICKS_COUNT = 100  # around 1.7s

    def __init__(self, func, timeout_limit, awaited_listener=None, on_timeout=None):
        # type: (Callable, int, Callable, Callable) -> None
        """timeout_limit in ms"""
        super(TimeoutLimit, self).__init__()
        self.func = func
        self.awaited_listener = awaited_listener
        self.on_timeout = on_timeout
        Scheduler.wait(timeout_limit * self.TICKS_COUNT, self._after_timeout)
        self.executed = False
        self.timed_out = False

    def __repr__(self, **k):
        # type: (Any) -> str
        output = "%s" % get_callable_repr(self.func)
        if self.awaited_listener:
            output += " (waiting for listener call %s)" % get_callable_repr(self.awaited_listener)
        return output

    def __call__(self, *a, **k):
        # type: (Any, Any) -> None
        if self.timed_out:
            Logger.warning("Tried to execute function after timeout: %s" % self)
            return

        self.executed = True
        self.func(*a, **k)

    def _after_timeout(self):
        # type: () -> None
        if self.timed_out:
            raise Protocol0Error("Tried to execute timeout function twice: %s" % self)

        if self.executed:
            return

        self.timed_out = True
        if self.on_timeout:
            self.on_timeout()
            return
        else:
            Logger.error("Timeout reached for %s" % self)

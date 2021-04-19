from typing import Any, Callable

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.utils import get_callable_name


class TimeoutLimit(AbstractObject):
    TICKS_COUNT = 100

    def __init__(self, func, timeout_limit, awaited_listener=None, on_timeout=None, *a, **k):
        # type: (Callable, int, Callable, Callable, Any, Any) -> None
        """ timeout_limit in ms """
        super(TimeoutLimit, self).__init__(*a, **k)
        self.func = func
        self.awaited_listener = awaited_listener
        self.on_timeout = on_timeout
        self.parent._wait(timeout_limit * self.TICKS_COUNT, self._after_timeout)
        self.executed = False
        self.timed_out = False

    def __repr__(self):
        # type: () -> str
        output = "%s: %s" % (id(self), get_callable_name(self.func))
        if self.awaited_listener:
            output += " (waiting for listener call %s)" % get_callable_name(self.awaited_listener)
        return output

    def __call__(self, *a, **k):
        # type: (Any, Any) -> None
        if self.timed_out:
            self.parent.log_error("Executed function after timeout: %s" % self)
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
            self.parent.log_error("Timeout reached for %s" % self)

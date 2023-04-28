import inspect
import time
from collections import defaultdict
from functools import wraps, partial

from typing import Any, Callable, Optional, Tuple

from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.func import get_callable_repr
from protocol0.domain.shared.utils.utils import clamp
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.types import Func


def defer(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        from protocol0.domain.shared.scheduler.Scheduler import Scheduler

        Scheduler.defer(partial(func, *a, **k))
        return None

    return decorate


def debounce(duration=100):
    # type: (int) -> Func
    """duration: ms"""

    def wrap(func):
        # type: (Func) -> Func
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> None
            object_source = a[0] if inspect.ismethod(func) else decorate

            decorate.count[object_source] += 1  # type: ignore[attr-defined]

            from protocol0.domain.shared.scheduler.Scheduler import Scheduler

            Scheduler.wait_ms(duration, partial(execute, func, *a, **k))

        decorate.count = defaultdict(int)  # type: ignore[attr-defined]

        def execute(real_func, *a, **k):
            # type: (Callable, Any, Any) -> Any
            object_source = a[0] if inspect.ismethod(real_func) else decorate
            decorate.count[object_source] -= 1  # type: ignore[attr-defined]
            if decorate.count[object_source] == 0:  # type: ignore[attr-defined]
                return real_func(*a, **k)

        return decorate

    return wrap


class Throttler(object):
    def __init__(self, func, duration):
        # type: (Callable, int) -> None
        self._func = func
        self._func_repr = get_callable_repr(func)
        self._duration = duration
        self._last_res = None
        self._last_args = None  # type: Optional[Tuple[Any, Any]]
        self._throttled = False

    def execute(self, *a, **k):
        # type: (Any, Any) -> Any
        if not self._throttled:
            self._last_res = self._func(*a, **k)
            Scheduler.wait_ms(self._duration, self._on_duration_elapsed)
            self._throttled = True
            return self._last_res
        else:
            Logger.warning("%s throttled" % self._func_repr)
            self._last_args = (a, k)
            return self._last_res

    def _on_duration_elapsed(self):
        # type: () -> None
        self._throttled = False
        if self._last_args is not None:
            a, k = self._last_args
            self._last_args = None
            self.execute(*a, **k)


def throttle(duration=100):
    # type: (int) -> Func
    """duration in ms"""

    def wrap(func):
        # type: (Func) -> Func
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> Any
            object_source = a[0] if inspect.ismethod(func) else decorate

            return decorate._throttler[object_source].execute(*a, **k)  # type: ignore[attr-defined]

        decorate._throttler = defaultdict(lambda: Throttler(func, duration))  # type: ignore[attr-defined]

        return decorate

    return wrap


def accelerate(func):
    # type: (Func) -> Func
    """
        Function used to soft accelerate parameter scrolling as done in the hardware
        Function that will transmit the number of times it was called during the last second
        The count is given in the factor keyword argument
        Useful for implementing input acceleration
    """
    # in ms : the duration considered for increasing the acceleration factor
    ACCELERATION_ACTIVATION_DURATION = 700
    # above this is too fast
    MAX_ACCELERATION = 20
    # number of calls allowed before acceleration starts
    FINE_TUNING_RANGE = 2

    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        object_source = a[0] if inspect.ismethod(func) else decorate

        last_calls = decorate.last_calls[object_source]    # type: ignore[attr-defined]
        last_calls.append(time.time())

        duration_second = float(ACCELERATION_ACTIVATION_DURATION) / 1000
        last_calls = list(filter(lambda t: t >= time.time() - duration_second, last_calls))
        decorate.last_calls[object_source] = last_calls  # type: ignore[attr-defined]

        acceleration = len(last_calls) - FINE_TUNING_RANGE + 1
        k["factor"] = clamp(acceleration, 1, MAX_ACCELERATION)
        return func(*a, **k)

    decorate.last_calls = defaultdict(list)  # type: ignore[attr-defined]

    return decorate

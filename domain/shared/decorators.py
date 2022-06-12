from collections import defaultdict
from functools import wraps, partial

from typing import Any, Callable, Optional

from protocol0.domain.shared.utils import is_method, get_callable_repr
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


def lock(func):
    # type: (Func) -> Func
    from protocol0.shared.sequence.Sequence import Sequence

    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> Optional[Sequence]
        object_source = a[0] if is_method(func) else decorate
        if decorate.lock[object_source]:  # type: ignore[attr-defined]
            return None

        decorate.lock[object_source] = True  # type: ignore[attr-defined]

        def unlock():
            # type: ()  -> None
            decorate.lock[object_source] = False  # type: ignore[attr-defined]

        seq = Sequence()
        seq.add(partial(func, *a, **k))
        seq.add(unlock)
        return seq.done()

    decorate.lock = defaultdict(int)  # type: ignore[attr-defined]

    return decorate


def debounce(duration=100):
    # type: (int) -> Func
    """duration: ms"""

    def wrap(func):
        # type: (Func) -> Func
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> None
            object_source = a[0] if is_method(func) else decorate
            decorate.count[object_source] += 1  # type: ignore[attr-defined]
            from protocol0.domain.shared.scheduler.Scheduler import Scheduler
            Scheduler.wait_ms(duration, partial(execute, func, *a, **k))

        decorate.count = defaultdict(int)  # type: ignore[attr-defined]

        def execute(real_func, *a, **k):
            # type: (Callable, Any, Any) -> Any
            object_source = a[0] if is_method(real_func) else decorate
            decorate.count[object_source] -= 1  # type: ignore[attr-defined]
            if decorate.count[object_source] == 0:  # type: ignore[attr-defined]
                return real_func(*a, **k)

        return decorate

    return wrap


def throttle(duration=100):
    # type: (int) -> Func
    """duration in ms"""
    def wrap(func):
        # type: (Func) -> Func
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> Any
            object_source = a[0] if is_method(func) else decorate

            if decorate.paused[object_source] and k.get("throttle", True):  # type: ignore[attr-defined]
                Logger.warning("%s throttled" % get_callable_repr(func))
                return

            decorate.paused[object_source] = True  # type: ignore[attr-defined]
            res = func(*a, **k)

            def activate():
                # type: () -> None
                decorate.paused[object_source] = False  # type: ignore[attr-defined]

            from protocol0.domain.shared.scheduler.Scheduler import Scheduler
            Scheduler.wait_ms(duration, activate)
            return res

        decorate.paused = defaultdict(lambda: False)  # type: ignore[attr-defined]

        return decorate

    return wrap


def handle_error(func):
    # type: (Func) -> Func
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> Any
        # noinspection PyBroadException
        try:
            return func(*a, **k)
        except Exception:
            from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
            from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
            DomainEventBus.emit(ErrorRaisedEvent())
            # raise e

    return decorate

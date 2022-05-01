from collections import defaultdict
from functools import wraps, partial

from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from typing import Any, Callable, TYPE_CHECKING, Optional

from protocol0.domain.shared.utils import is_method
from protocol0.shared.types import Func

if TYPE_CHECKING:
    from protocol0.shared.sequence.CallbackDescriptor import CallbackDescriptor


def p0_subject_slot(event):
    # type: (str) -> Callable[[Callable], CallbackDescriptor]
    """
    Drop in replacement of _Framework subject_slot decorator
    Extends its behavior to allow the registration of callbacks that will execute after the decorated function finished
    By default the callbacks executions are deferred to prevent the dreaded "Changes cannot be triggered by notifications. You will need to defer your response"
    immediate=True executes the callbacks immediately (synchronously)

    This decorator / callback registration is mainly used by the Sequence pattern
    It allows chaining functions by reacting to listeners being triggered and is paramount to executing asynchronous sequence of actions
    Sequence.wait_for_listener(<@p0_subject_slot<listener>>) will actually register a callback on the decorated <listener>.
    This callback will resume the sequence when executed.
    """

    def wrap(func):
        # type: (Callable) -> CallbackDescriptor
        def decorate(*a, **k):
            # type: (Any, Any) -> None
            func(*a, **k)

        decorate.original_func = func  # type: ignore[attr-defined]

        callback_descriptor = has_callback_queue()(_framework_subject_slot(event)(decorate))

        return callback_descriptor

    return wrap


def has_callback_queue():
    # type: () -> Callable[[Callable], CallbackDescriptor]
    def wrap(func):
        # type: (Callable) -> CallbackDescriptor
        from protocol0.shared.sequence.CallbackDescriptor import CallbackDescriptor

        return CallbackDescriptor(func)

    return wrap


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


def debounce(wait_time=100):
    # type: (float) -> Func
    """ here we make the method dynamic """

    def wrap(func):
        # type: (Func) -> Func
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> None
            object_source = a[0] if is_method(func) else decorate
            decorate.count[object_source] += 1  # type: ignore[attr-defined]
            from protocol0.domain.shared.scheduler.Scheduler import Scheduler
            Scheduler.wait_seconds(float(wait_time) / 1000, partial(execute, func, *a, **k))

        decorate.count = defaultdict(int)  # type: ignore[attr-defined]

        def execute(real_func, *a, **k):
            # type: (Callable, Any, Any) -> Any
            object_source = a[0] if is_method(real_func) else decorate
            decorate.count[object_source] -= 1  # type: ignore[attr-defined]
            if decorate.count[object_source] == 0:  # type: ignore[attr-defined]
                return real_func(*a, **k)

        return decorate

    return wrap


def throttle(wait_time=100):
    # type: (int) -> Func
    def wrap(func):
        # type: (Func) -> Func
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> Any
            object_source = a[0] if is_method(func) else decorate

            if decorate.paused[object_source] and k.get("throttle", True):  # type: ignore[attr-defined]
                return

            decorate.paused[object_source] = True  # type: ignore[attr-defined]
            res = func(*a, **k)

            def activate():
                # type: () -> None
                decorate.paused[object_source] = False  # type: ignore[attr-defined]

            from protocol0.domain.shared.scheduler.Scheduler import Scheduler
            Scheduler.wait(wait_time, activate)
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
            from protocol0.domain.shared.DomainEventBus import DomainEventBus
            from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
            DomainEventBus.emit(ErrorRaisedEvent())
            # raise e

    return decorate

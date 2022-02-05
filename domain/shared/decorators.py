from collections import defaultdict
from functools import wraps, partial

from typing import Any, Callable

from protocol0.domain.sequence.callback_descriptor import CallbackDescriptor
from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from protocol0.domain.shared.utils import is_method


def p0_subject_slot(event):
    # type: (str) -> Callable[[Callable], CallbackDescriptor]
    """
    Drop in replacement of _Framework subject_slot decorator
    Extends its behavior to allow the registration of callbacks that will execute after the decorated function finished
    By default the callbacks execution is deferred to prevent the dreaded "Changes cannot be triggered by notifications. You will need to defer your response"
    immediate=True executes the callbacks immediately (synchronously)

    This decorator / callback registration is mainly used by the Sequence pattern
    It allows chaining functions by reacting to listeners being triggered and is paramount to executing asynchronous sequence of actions
    Sequence.add(complete_on=<@p0_subject_slot<listener>> will actually registers a callback on the decorated <listener>.
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
        from protocol0.domain.sequence.callback_descriptor import CallbackDescriptor

        return CallbackDescriptor(func)

    return wrap


def defer(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0

        Protocol0.SELF.defer(partial(func, *a, **k))
        return None

    return decorate


def debounce(wait_time=100):
    # type: (int) -> Callable
    """ here we make the method dynamic """

    def wrap(func):
        # type: (Callable) -> Callable
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> None
            object_source = a[0] if is_method(func) else decorate
            decorate.count[object_source] += 1  # type: ignore[attr-defined]
            from protocol0 import Protocol0

            Protocol0.SELF.wait(wait_time, partial(execute, func, *a, **k))

        decorate.count = defaultdict(int)

        def execute(real_func, *a, **k):
            # type: (Callable, Any, Any) -> Any
            object_source = a[0] if is_method(real_func) else decorate
            decorate.count[object_source] -= 1  # type: ignore[attr-defined]
            if decorate.count[object_source] == 0:  # type: ignore[attr-defined]
                return real_func(*a, **k)

        return decorate

    return wrap


def throttle(wait_time=100):
    # type: (int) -> Callable
    def wrap(func):
        # type: (Callable) -> Callable
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> Any
            object_source = a[0] if is_method(func) else decorate

            if decorate.paused[object_source] and k.get("throttle", True):
                return

            decorate.paused[object_source] = True
            res = func(*a, **k)

            def activate():
                # type: () -> None
                decorate.paused[object_source] = False

            from protocol0 import Protocol0
            Protocol0.SELF.wait(wait_time, activate)
            return res

        decorate.paused = defaultdict(lambda: False)  # type: ignore[attr-defined]

        return decorate

    return wrap

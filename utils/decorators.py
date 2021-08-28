from functools import partial, wraps

from typing import TYPE_CHECKING, Any, Callable

from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from protocol0.utils.utils import is_method

if TYPE_CHECKING:
    from protocol0.components.Push2Manager import Push2Manager
    from protocol0.utils.callback_descriptor import CallbackDescriptor


def push2_method(defer=True):
    # type: (bool) -> Callable
    def wrap(func):
        # type: (Callable) -> Callable
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (Push2Manager, Any, Any) -> None
            # check hasattr in case the push2 is turned off during a set
            if not self.push2 or not hasattr(self.push2, "_initialized") or not self.push2._initialized:
                return

            def execute():
                # type: () -> None
                with self.push2.component_guard():
                    func(self, *a, **k)

            if defer:
                self.parent.defer(execute)
            else:
                execute()

        return decorate

    return wrap


def defer(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0

        Protocol0.SELF.defer(partial(func, *a, **k))

    return decorate


EXPOSED_P0_METHODS = {}


def api_exposable_class(cls):
    for name, method in cls.__dict__.iteritems():
        if hasattr(method, "api_exposed"):
            EXPOSED_P0_METHODS[name] = cls
    return cls


def api_exposed(func):
    # type: (Callable) -> Callable
    func.api_exposed = True
    return func


def poll(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0

        func(*a, **k)
        Protocol0.SELF.defer(partial(decorate, *a, **k))

    return decorate


def retry(retry_count=3, interval=3):
    # type: (int, int) -> Callable
    def wrap(func):
        # type: (Callable) -> Callable
        @wraps(func)
        def decorate(*a, **k):
            # type: (Any, Any) -> None
            from protocol0 import Protocol0

            # noinspection PyBroadException
            try:
                func(*a, **k)
            except Exception:
                if decorate.count == decorate.retry_count:  # type: ignore[attr-defined]
                    return
                Protocol0.SELF._wait(pow(2, decorate.count) * interval,
                                     partial(func, *a, **k))  # type: ignore[attr-defined]
                decorate.count += 1  # type: ignore[attr-defined]

        decorate.count = 0  # type: ignore[attr-defined]
        decorate.retry_count = retry_count  # type: ignore[attr-defined]

        return decorate

    return wrap


def p0_subject_slot(event, immediate=False):
    # type: (str, bool) -> Callable[[Callable], CallbackDescriptor]
    """
    Drop in replacement of _Framework subject_slot decorator
    Allows the registration of callbacks to be execute after the decorated function
    By default the callbacks are deferred to handle the notification change error
    immediate calls the callbacks synchronously
    This decorator is used by the Sequence pattern and allows the sequence to wait for a change to happen
    That is it waits for a listener to be triggered.
    With this, a callback to continue the sequence can be automatically attached to any listener without more hassle
    """

    def wrap(func):
        # type: (Callable) -> CallbackDescriptor
        def decorate(*a, **k):
            # type: (Any, Any) -> None
            func(*a, **k)

        decorate.original_func = func  # type: ignore[attr-defined]

        callback_descriptor = has_callback_queue(immediate)(_framework_subject_slot(event)(decorate))

        return callback_descriptor

    return wrap


def has_callback_queue(immediate=False):
    # type: (bool) -> Callable[[Callable], CallbackDescriptor]
    def wrap(func):
        # type: (Callable) -> CallbackDescriptor
        from protocol0.utils.callback_descriptor import CallbackDescriptor

        return CallbackDescriptor(func, immediate)

    return wrap


def log(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        func_name = func.__name__
        args = [str(arg) for arg in a] + ["%s=%s" % (key, str(value)) for (key, value) in k.items()]
        if is_method(func):
            func_name = "%s.%s" % (a[0].__class__.__name__, func_name)
            args = args[1:]
        message = func_name + "(%s)" % (", ".join([str(arg) for arg in args]))

        from protocol0 import Protocol0

        Protocol0.SELF.log_info("-- %s" % message, debug=False)
        func(*a, **k)

    return decorate


def handle_error(func):
    # type: (Callable) -> Callable
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        try:
            func(*a, **k)
        except Exception as e:
            from protocol0 import Protocol0

            Protocol0.SELF.errorManager.handle_error(e)

    return decorate

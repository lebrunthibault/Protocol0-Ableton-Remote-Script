import time
from collections import defaultdict
from functools import partial, wraps

from typing import TYPE_CHECKING, Any, Callable

from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from a_protocol_0.utils.utils import is_method

if TYPE_CHECKING:
    from a_protocol_0.components.Push2Manager import Push2Manager
    from a_protocol_0.lom.AbstractObject import AbstractObject
    from a_protocol_0.sequence.Sequence import Sequence
    from a_protocol_0.utils.callback_descriptor import CallbackDescriptor


def push2_method(defer=True):
    def wrap(func):
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (Push2Manager, Any, Any) -> None
            # check hasattr in case the push2 is turned off during a set
            if not self.push2 or not hasattr(self.push2, "_initialized") or not self.push2._initialized:
                return

            def execute():
                with self.push2.component_guard():
                    func(self, *a, **k)

            if defer:
                self.parent.defer(execute)
            else:
                execute()

        return decorate

    return wrap


def defer(func):
    @wraps(func)
    def decorate(*a, **k):
        from a_protocol_0 import Protocol0

        Protocol0.SELF.defer(partial(func, *a, **k))

    return decorate


def retry(retry_count=3, interval=3):
    def wrap(func):
        @wraps(func)
        def decorate(*a, **k):
            from a_protocol_0 import Protocol0

            try:
                func(*a, **k)
            except Exception:
                if decorate.count == decorate.retry_count:
                    return
                Protocol0.SELF._wait(pow(2, decorate.count) * interval, partial(func, *a, **k))
                decorate.count += 1

        decorate.count = 0
        decorate.retry_count = retry_count

        return decorate

    return wrap


def debounce(wait_time=200):
    """ here we make the method dynamic """

    def wrap(func):
        @wraps(func)
        def decorate(*a, **k):
            index = a[0] if is_method(func) else decorate
            wait_time = 0 if k.get("disable_debounce", False) else decorate.wait_time[index]
            k.pop("disable_debounce", None)
            decorate.count[index] += 1
            from a_protocol_0 import Protocol0

            Protocol0.SELF._wait(wait_time, partial(execute, func, *a, **k))

        decorate.count = defaultdict(int)
        decorate.wait_time = defaultdict(lambda: wait_time)
        decorate.func = func

        def execute(func, *a, **k):
            index = a[0] if is_method(func) else decorate
            decorate.count[index] -= 1
            if decorate.count[index] == 0:
                func(*a, **k)

        return decorate

    return wrap


def throttle(wait_time=2, max_execution_count=3):
    def wrap(func):
        @wraps(func)
        def decorate(*a, **k):
            index = a[0] if is_method(func) else decorate
            exec_time = time.time()
            if (
                len([t for t in decorate.execution_times[index][-3:] if exec_time - t < decorate.wait_time])
                == decorate.max_execution_count
            ):
                return
            func(*a, **k)
            decorate.execution_times[index].append(time.time())

        decorate.wait_time = wait_time
        decorate.max_execution_count = max_execution_count
        decorate.execution_times = defaultdict(lambda: [])
        decorate.func = func

        return decorate

    return wrap


def button_action(auto_arm=False, log_action=True):
    """ decorator on an action to configure logging and arming (for now) """

    def wrap(func):
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (AbstractObject, Any, Any) -> Sequence
            from a_protocol_0.sequence.Sequence import Sequence

            seq = Sequence()
            if auto_arm and not self.song.current_track.is_armed:
                seq.add(self.song.current_track.arm, silent=True)

            seq.add(partial(func, self, **k))

            return seq.done()

        return decorate

    return wrap


def p0_subject_slot(event, immediate=False):
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
        def decorate(*a, **k):
            func(*a, **k)

        decorate.original_func = func

        callback_descriptor = has_callback_queue(immediate)(_framework_subject_slot(event)(decorate))

        # noinspection PyTypeChecker
        return wraps(func)(callback_descriptor)

    return wrap


def has_callback_queue(immediate=False):
    def wrap(func):
        # type: (Callable) -> CallbackDescriptor
        from a_protocol_0.utils.callback_descriptor import CallbackDescriptor

        return CallbackDescriptor(func, immediate)

    return wrap


def _arg_to_string(arg):
    if isinstance(arg, str):
        return '"%s"' % arg
    else:
        return arg


def log(func):
    @wraps(func)
    def decorate(*a, **k):
        func_name = func.__name__
        args = [_arg_to_string(arg) for arg in a] + [
            "%s=%s" % (key, _arg_to_string(value)) for (key, value) in k.items()
        ]
        if is_method(func):
            func_name = "%s.%s" % (a[0].__class__.__name__, func_name)
            args = args[1:]
        message = func_name + "(%s)" % (", ".join([str(arg) for arg in args]))

        from a_protocol_0 import Protocol0

        Protocol0.SELF.log_info("-- %s" % message, debug=False)
        func(*a, **k)

    return decorate


def handle_error(func):
    @wraps(func)
    def decorate(*a, **k):
        try:
            func(*a, **k)
        except Exception as e:
            from a_protocol_0 import Protocol0

            Protocol0.SELF.errorManager.handle_error(e)

    return decorate

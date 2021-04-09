import time
from collections import defaultdict
from functools import partial, wraps

from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.utils.utils import is_method, get_callable_name

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.components.Push2Manager import Push2Manager
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.AbstractObject import AbstractObject


def push2_method(defer=True):
    def wrap(func):
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (Push2Manager) -> None
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


def is_change_deferrable(func):
    @wraps(func)
    def decorate(*a, **k):
        try:
            func(*a, **k)
        except RuntimeError as e:
            if "Changes cannot be triggered by notifications" in str(e):
                from a_protocol_0 import Protocol0
                Protocol0.SELF.defer(partial(func, *a, **k))
            else:
                raise e

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
            if len([t for t in decorate.execution_times[index][-3:] if
                    exec_time - t < decorate.wait_time]) == decorate.max_execution_count:
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
            # type: (AbstractObject) -> None
            if log_action:
                self.parent.log_notice("Executing %s" % func.__name__)
            from a_protocol_0.sequence.Sequence import Sequence
            seq = Sequence()
            if auto_arm and not self.song.current_track.arm:
                seq.add(self.song.current_track.action_arm, silent=True)

            seq.add(partial(func, self, **k))

            return seq.done()

        return decorate

    return wrap


def p0_subject_slot(event):
    def wrap(func):
        def decorate(*a, **k):
            func(*a, **k)

        decorate.original_func = func

        return wraps(func)(has_callback_queue(_framework_subject_slot(event)(decorate)))

    return wrap


def has_callback_queue(func):
    from a_protocol_0.utils.callback_descriptor import CallbackDescriptor
    return CallbackDescriptor(func)


def catch_and_stop(func):
    @wraps(func)
    def decorate(*a, **k):
        from a_protocol_0 import Protocol0
        song = Protocol0.SELF.protocol0_song
        if song.errored:
            return
        try:
            func(*a, **k)
        except (Exception, RuntimeError) as e:
            raise Protocol0Error("Error on %s" % get_callable_name(func))

    return decorate


def _arg_to_string(arg):
    if isinstance(arg, str):
        return '"%s"' % arg
    else:
        return arg


def log(func):
    @wraps(func)
    def decorate(*a, **k):
        func_name = func.__name__
        args = [_arg_to_string(arg) for arg in a] + ["%s=%s" % (key, _arg_to_string(value)) for (key, value) in
                                                     k.items()]
        if is_method(func):
            func_name = "%s.%s" % (a[0].__class__.__name__, func_name)
            args = args[1:]
        message = func_name + "(%s)" % (", ".join([str(arg) for arg in args]))

        from a_protocol_0 import Protocol0
        Protocol0.SELF.log_info("-- %s" % message, debug=False)
        func(*a, **k)

    return decorate

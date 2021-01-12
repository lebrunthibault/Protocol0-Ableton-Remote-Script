import traceback
from collections import defaultdict
from functools import partial, wraps

from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from a_protocol_0.sequence.SequenceState import SequenceState
from a_protocol_0.utils.log import log_ableton
from a_protocol_0.utils.utils import is_method, deduplicate_list, get_callable_name

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
    # noinspection PyUnresolvedReferences
    from a_protocol_0.components.Push2Manager import Push2Manager


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


def wait(wait_time):
    def wrap(func):
        @wraps(func)
        def decorate(*a, **k):
            from a_protocol_0 import Protocol0
            Protocol0.SELF._wait(wait_time, partial(func, *a, **k))

        return decorate

    return wrap


def timeout_limit(func, awaited_func, timeout_limit, on_timeout=None):
    # type: (callable, callable, float, callable) -> callable
    from a_protocol_0 import Protocol0

    @wraps(func)
    def decorate(timeout_execution=False, *a, **k):
        if decorate.executed:
            return
        if timeout_execution:
            Protocol0.SELF.log_error("Timeout reached for function %s, not executing %s" % (
            get_callable_name(awaited_func), get_callable_name(func)))
            if on_timeout:
                on_timeout()
                return
        func(*a, **k)
        decorate.executed = True

    decorate.executed = False
    Protocol0.SELF._wait(timeout_limit, partial(decorate, timeout_execution=True))

    return decorate


def retry(retry_count=2, interval=1):
    def wrap(func):
        @wraps(func)
        def decorate(*a, **k):
            from a_protocol_0 import Protocol0
            try:
                func(*a, **k)
            except Exception:
                if decorate.count == decorate.retry_count:
                    Protocol0.SELF.log_error("Retry error on %s" % decorate)
                    return
                Protocol0.SELF._wait(pow(2, decorate.count) * interval, partial(func, *a, **k))
                decorate.count += 1

        decorate.count = 0
        decorate.retry_count = retry_count

        return decorate

    return wrap


def debounce(wait_time=2):
    def wrap(func):
        @wraps(func)
        def decorate(*a, **k):
            index = a[0] if is_method(func) else decorate
            decorate.count[index] += 1
            from a_protocol_0 import Protocol0
            Protocol0.SELF._wait(decorate.wait_time[index], partial(execute, func, *a, **k))

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


def button_action(auto_arm=False, log_action=True, auto_undo=True):
    def wrap(func):
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (AbstractControlSurfaceComponent) -> None
            if log_action:
                self.parent.log_info("Executing " + func.__name__)
            self.song.begin_undo_step()
            try:
                if auto_arm:
                    self.song.unfocus_all_tracks()
                    if not self.song.current_track.arm:
                        self.song.current_track.action_arm()
                func(self, **k)
            except (Exception, RuntimeError):
                self.parent.log_error(traceback.format_exc())
                return
            if auto_undo:
                self.parent.defer(self.song.end_undo_step)

        return decorate

    return wrap


def subject_slot(event):
    def wrap(func):
        @wraps(func)
        @has_callback_queue
        @_framework_subject_slot(event)
        @wraps(func)
        def decorate(*a, **k):
            func(*a, **k)

        return decorate

    return wrap


class CallbackDescriptor(object):
    """ Inspired from _Framework @instance_method, adds the callback queue """

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self._func = func
        self._data_name = u'%s_%d_decorated_instance' % (func.__name__, id(self))

    def __get__(self, obj, cls=None):
        if obj is None:
            return
        try:
            return obj.__dict__[self._data_name]
        except KeyError:
            # checking if we are on top of a subject_slot decorator
            if bool(getattr(self._func, "_data_name", None)):
                decorated = self._func.__get__(obj)  # calling inner descriptor. decorated is a SubjectSlot
                decorated.listener = self.callback_wrapper(decorated)
            else:
                decorated = self.callback_wrapper(partial(self._func, obj))
                # here we set _callbacks directly on callback_caller
            decorated._callbacks = []
            decorated._has_callback_queue = True
            obj.__dict__[self._data_name] = decorated  # setting decorated on outer descriptor
            return decorated  # decorated is the outer most function replacing the decorated method

    def callback_wrapper(self, decorated):
        def callback_caller(*a, **k):
            res = decorated(*a, **k)
            from a_protocol_0.sequence.Sequence import Sequence
            if isinstance(res, Sequence) and res._state != SequenceState.TERMINATED:
                res.terminated_callback = _execute_callbacks
            else:
                # pass
                _execute_callbacks()

        callback_caller.__name__ = get_callable_name(decorated)

        def _execute_callbacks():
            callback_provider = decorated if hasattr(decorated, "_callbacks") else callback_caller
            callback_provider.func = decorated
            # callbacks deduplication (useful to mitigate e.g. double encoder click)
            for callback in deduplicate_list(callback_provider._callbacks):
                callback()
            callback_provider._callbacks = []

        return callback_caller


def has_callback_queue(func):
    return CallbackDescriptor(func)


def catch_and_log(func):
    @wraps(func)
    def decorate(*a, **k):
        try:
            func(*a, **k)
        except Exception:
            from a_protocol_0 import Protocol0
            Protocol0.SELF.log_error(traceback.format_exc())
            return

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
        message = func_name + "(%s)" % (", ".join(args))

        from a_protocol_0 import Protocol0
        Protocol0.SELF.log_info(message, debug=False)
        func(*a, **k)

    return decorate

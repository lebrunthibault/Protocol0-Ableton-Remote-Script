import traceback
from collections import defaultdict
from functools import partial, wraps
from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from a_protocol_0.utils.log import log_ableton
from a_protocol_0.utils.utils import _arg_count, is_method

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
                self.parent.log_info("---------------- " + func.__name__)
                self.parent.log_info("---------------- " + func.__name__)
                self.parent.log_info("---------------- " + func.__name__)
                self.parent.log_info("---------------- " + func.__name__)
                self.parent.log_info("---------------- " + func.__name__)
                self.parent.log_info("Executing " + func.__name__)

            self.song.begin_undo_step()
            try:
                if auto_arm:
                    self.song.unfocus_all_tracks()
                    if not self.song.current_track.arm:
                        self.song.current_track.action_arm()
                func(self, **k)
            except Exception:
                self.parent.log_info(traceback.format_exc())
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
        def decorate(*a, **k):
            func(*a, **k)

        return decorate
    return wrap


def has_callback_queue(func):
    """ for now, should decorate subject_slot decorated methods """
    class CallbackDescriptor(object):
        """ Inspired from _Framework @instance_method, adds the callback queue """
        def __init__(self):
            self.__name__ = func.__name__
            self.__doc__ = func.__doc__
            self._data_name = u'%s_%d_decorated_instance' % (func.__name__, id(self))

        def __get__(self, obj, cls=None):

            if obj is None:
                return
            try:
                return obj.__dict__[self._data_name]
            except KeyError:
                # checking if we are on top of a subject_slot decorator
                if bool(getattr(func, "_data_name", None)):
                    decorated = func.__get__(obj)  # calling inner descriptor. decorated is a SubjectSlot
                    decorated.listener = self.callback_wrapper(decorated)
                else:
                    decorated = self.callback_wrapper(partial(func, obj))
                    # here we set _callbacks directly on callback_caller
                decorated._callbacks = []
                obj.__dict__[self._data_name] = decorated  # setting decorated on outer descriptor
                return decorated  # decorated is the outer most function replacing the decorated method

        def callback_wrapper(self, decorated):
            def callback_caller(*a, **k):
                from a_protocol_0.Protocol0 import Protocol0
                decorated(*a, **k)

                callback_provider = decorated if hasattr(decorated, "_callbacks") else callback_caller
                # callbacks deduplication (useful to mitigate e.g. double encoder click)
                for callback in set(callback_provider._callbacks):
                    Protocol0.SELF.defer(partial(callback, getattr(decorated, "subject", "toto")) if _arg_count(callback) == 1 else callback)
                    # Protocol0.SELF.defer(partial(callback, decorated.subject) if hasattr(decorated, "subject") and _arg_count(callback) == 1 else callback)
                callback_provider._callbacks = []

            return callback_caller

    return CallbackDescriptor()


def catch_and_log(func):
    @wraps(func)
    def decorate(*a, **k):
        try:
            func(*a, **k)
        except Exception:
            log_ableton(traceback.format_exc())
            return

    return decorate


def log(func):
    @wraps(func)
    def decorate(*a, **k):
        log_ableton((func, a, k))
        func(*a, **k)

    return decorate

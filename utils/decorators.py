import traceback
from collections import defaultdict
from functools import partial, wraps
from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot as _framework_subject_slot
from a_protocol_0.utils.utils import _arg_count

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
    # noinspection PyUnresolvedReferences
    from a_protocol_0.components.Push2Manager import Push2Manager


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


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
    def decorate(self, *a, **k):
        # type: (AbstractControlSurfaceComponent) -> None
        self.parent.defer(partial(func, self, *a, **k))

    return decorate


def wait(wait_time):
    def wrap(func):
        @wraps(func)
        def decorate(*a, **k):
            from a_protocol_0 import Protocol0
            Protocol0.SELF._wait(wait_time, partial(func, *a, **k))

        return decorate

    return wrap


def debounce(func):
    @wraps(func)
    def decorate(self, *a, **k):
        # type: (AbstractControlSurfaceComponent) -> None
        decorate.count[self] += 1
        self.parent._wait(decorate.wait_time[self], partial(execute, func, self, *a, **k))

    decorate.count = defaultdict(int)
    decorate.wait_time = defaultdict(lambda: 3)

    def execute(func, self, *a, **k):
        decorate.count[self] -= 1
        if decorate.count[self] == 0:
            func(self, *a, **k)

    return decorate


def button_action(auto_arm=False, log_action=True):
    def wrap(func):
        @wraps(func)
        def decorate(self, *a, **k):
            # type: (AbstractControlSurfaceComponent) -> None
            if log_action:
                self.parent.log_info("Executing " + func.__name__)
            try:
                if auto_arm:
                    self.song.unfocus_all_tracks()
                    if not self.song.current_track.arm:
                        self.song.current_track.action_arm()
                func(self, **k)
            except Exception:
                self.parent.log_info(traceback.format_exc())
                return

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
            self.parent = None
            self._data_name = u'%s_%d_decorated_instance' % (func.__name__, id(self))

        def setup_decorated_function(self, decorated, obj):
            """ initialisation code on first object lookup """
            decorated.listener = self.listener(decorated)
            decorated._callbacks = []

        def __get__(self, obj, cls=None):
            if obj is None:
                return
            try:
                return obj.__dict__[self._data_name]
            except KeyError:
                decorated = func.__get__(obj)  # calling inner descriptor. creating decorated which is is a SubjectSlot
                obj.__dict__[self._data_name] = decorated  # setting decorated on outer descriptor
                self.setup_decorated_function(decorated, obj)
                return decorated

        def listener(self, decorated):
            def decorate(*a, **k):
                from a_protocol_0.Protocol0 import Protocol0
                self.parent = self.parent or Protocol0.SELF
                decorated(*a, **k)
                for callback in decorated._callbacks:
                    self.parent.defer(callback if _arg_count(callback) == 0 else partial(callback, decorated.subject))
                decorated._callbacks = []

            return decorate

    return CallbackDescriptor()


def catch_and_log(func):
    @wraps(func)
    def decorate(self, *a, **k):
        # type: (AbstractControlSurfaceComponent) -> None
        try:
            func(self, *a, **k)
        except Exception:
            self.parent.log_info(traceback.format_exc())
            return

    return decorate

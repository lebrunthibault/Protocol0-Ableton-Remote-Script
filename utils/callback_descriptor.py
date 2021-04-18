from collections import deque
from functools import partial

from typing import Any

from a_protocol_0.utils.log import log_ableton
from a_protocol_0.utils.utils import is_partial, get_callable_name


class CallbackDescriptor(object):
    """
    Inspired from _Framework @instance_method, adds a callback queue to any method or listener method
    The callback queue is going to be executed after Sequence termination in the listener
    if the listener executes async code
    Note: there is 2 cases :
        - @has_callback_queue is dropped on a stock, undecorated method. This is the easy part.
        - @has_callback_queue is dropped on top of _Framework subject_slot :
            - We need to fetch the CallableSlotMixin from the decorated method
                (when the method is first accessed via __get__)
                Then we replace the listener with our own CallableWithCallbacks and
                we patch the subject slot mixin to look like CallableWithCallbacks
                The external interface is gonna be the same in both cases now
                (we use only add_callback, clear_callbacks and __call)
            - At method execution time (by _Framework code), we need to fetch
                the real undecorated method to get the result.
                Didn't really understand why _Framework code is not forwarding the result
                when calling the subject slot mixin ..
            - Then we get the best of both worlds, _Framework is doing its listener magic
                while we get full control on the function execution, response and _callbacks execution.
                Makes the decorator somehow complicated though ^^
    """

    def __init__(self, func, immediate, *a, **k):
        # type: (callable, bool, Any, Any) -> None
        super(CallbackDescriptor, self).__init__(*a, **k)
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self._func = func
        self._immediate = immediate
        self._wrapped = None

    def __repr__(self):
        return self._wrapped or (u"%s_%d_%s" % (get_callable_name(self._func), id(self), self.__class__.__name__))

    def __get__(self, obj, cls=None):
        if obj is None:
            return
        try:
            return obj.__dict__[id(self)]
        except KeyError:
            # checking if we are on top of a subject_slot decorator
            if bool(
                getattr(self._func, "_data_name", None)
            ):  # here we cannot do isinstance() as the Decorator class is in a closure
                self._wrapped = self._func.__get__(obj)  # calling inner descriptor. self._decorated is a SubjectSlot
                self._wrapped.listener = CallableWithCallbacks(self._wrapped, obj, self._immediate)

                # patching the wrapped function to have a coherent interface
                self._wrapped.add_callback = self._wrapped.listener.add_callback
                self._wrapped._callbacks = self._wrapped.listener._callbacks
                self._wrapped.clear_callbacks = self._wrapped.listener.clear_callbacks
            else:
                self._wrapped = CallableWithCallbacks(partial(self._func, obj), obj, self._immediate)

            obj.__dict__[id(self)] = self._wrapped  # caching self._wrapped
            return self._wrapped  # Outer most function replacing the decorated method


class CallableWithCallbacks(object):
    DEBUG_MODE = False

    def __init__(self, decorated, obj, immediate, *a, **k):
        # type: (callable, object, bool, Any, Any) -> None
        super(CallableWithCallbacks, self).__init__(*a, **k)
        self._real_name = None
        self._decorated = decorated
        self._obj = obj
        self._immediate = immediate
        self._callbacks = deque()

    def __repr__(self):
        return "%s (cwc %d)" % (get_callable_name(self._decorated, self._obj), id(self))

    def __call__(self, *a, **k):
        if is_partial(self._decorated):  # has_callback_queue on a stock method (only decorator set)
            res = self._decorated(*a, **k)
        else:
            # has_callback_queue on top of Framework's @subject_slot
            # let's fetch the inner function (bypass _Framework logic) to get the response
            res = self._decorated.function.func.original_func(self._obj, *a, **k)

        if self.DEBUG_MODE:
            log_ableton("listener res of %s : %s" % (self, res))
            log_ableton("callbacks of %s : %s" % (self, self._decorated._callbacks))

        from a_protocol_0.sequence.Sequence import Sequence

        if isinstance(res, Sequence) and not res.terminated:
            if res.errored:
                self._callbacks = deque()
            else:
                res.add(self._execute_callback_queue)
        else:
            self._execute_callback_queue()

        return res

    def add_callback(self, callback):
        # type: (callable, bool) -> None
        """
        we don't allow the same exact callback to be added. Mitigates stuff like double clicks
        defer is used for triggering callback after listeners and prevents change after notification error
        """
        if callback in self._callbacks:
            return
        self._callbacks.append(callback)
        if self.DEBUG_MODE:
            log_ableton("adding_callback to %s : %s" % (self, self._callbacks))

    def clear_callbacks(self):
        self._callbacks = deque()

    def _execute_callback_queue(self):
        """ execute callbacks and check if we defer this or not """
        if len(self._callbacks) == 0:
            return
        from a_protocol_0 import Protocol0

        Protocol0.SELF._wait(0 if self._immediate else 1, self._execute_callbacks)

    def _execute_callbacks(self):
        if self.DEBUG_MODE:
            log_ableton("_execute_callbacks of %s : %s" % (self, self._callbacks))
        while len(self._callbacks):
            self._callbacks.popleft()()

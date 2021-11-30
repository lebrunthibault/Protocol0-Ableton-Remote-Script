from collections import deque
from functools import partial

from typing import Callable, Deque, Optional, Any, cast, Type, Union

from protocol0.enums.SongLoadStateEnum import SongLoadStateEnum
from protocol0.utils.utils import get_callable_repr


class CallbackDescriptor(object):
    """
    Inspired from _Framework @instance_method, adds a callback queue to any method or listener method
    The callback queue is going to be executed after the decorated method returns
    if the listener executes in a sequence the callbacks are going to be executed after the sequence termination
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

    def __init__(self, func, immediate):
        # type: (Callable, bool) -> None
        super(CallbackDescriptor, self).__init__()
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self._func = func  # type: Any
        self._immediate = immediate
        self._wrapped = None  # type: Optional[Union[Any, CallableWithCallbacks]]

    def __repr__(self):
        # type: () -> str
        if self._wrapped:
            return str(self._wrapped)
        else:
            return "%s_%d_%s" % (get_callable_repr(self._func), id(self), self.__class__.__name__)

    def __get__(self, obj, cls=None):
        # type: (Any, Type[object]) -> Optional[Any]
        if obj is None:
            return None
        try:
            return obj.__dict__[id(self)]
        except KeyError:
            # checking if we are on top of a subject_slot decorator
            if bool(getattr(self._func, "_data_name", None)):
                # calling inner descriptor. self._wrapped is a SubjectSlot instance descriptor
                # noinspection PyUnresolvedReferences
                self._wrapped = self._func.__get__(obj)
                # noinspection PyUnresolvedReferences
                cwc = CallableWithCallbacks(
                    cast(Callable, partial(self._wrapped.function.func.original_func, obj)), self._immediate
                )
                self._wrapped.listener = cwc  # replacing the listener called by Live
                self._wrapped.function = cwc  # replacing the CallableSlotMixin.function for direct execution

                # patching the wrapped function to have a coherent interface
                self._wrapped.add_callback = cwc.add_callback  # type: ignore[assignment]
                self._wrapped._callbacks = cwc._callbacks
                self._wrapped.clear_callbacks = cwc.clear_callbacks  # type: ignore[assignment]
            else:
                self._wrapped = CallableWithCallbacks(partial(self._func, obj), self._immediate)

            obj.__dict__[id(self)] = self._wrapped  # caching self._wrapped
            return self._wrapped  # Outer most function replacing the decorated method


class CallableWithCallbacks(object):
    DEBUG_MODE = False

    def __init__(self, function, immediate):
        # type: (Callable, bool) -> None
        super(CallableWithCallbacks, self).__init__()
        self._function = function  # type: Any
        self._immediate = immediate
        self._callbacks = deque()  # type: Deque[Callable]

    def __repr__(self):
        # type: () -> str
        return "cwc %s" % get_callable_repr(self._function)

    def __call__(self, *a, **k):
        # type: (Any, Any) -> Any
        from protocol0 import Protocol0
        if Protocol0.SELF.protocol0_song.song_load_state == SongLoadStateEnum.LOADING and "listener" in str(self):
            return
        res = self._function(*a, **k)

        from protocol0.sequence.Sequence import Sequence

        if isinstance(res, Sequence) and not res.terminated:
            if res.errored:
                self._callbacks = deque()
            else:
                res.add(self._execute_callback_queue)
        else:
            self._execute_callback_queue()

        return res

    def add_callback(self, callback):
        # type: (Callable) -> None
        """
        we don't allow the same exact callback to be added. Mitigates stuff like double clicks
        defer is used for triggering callback after listeners and prevents change after notification error
        """
        if callback in self._callbacks:
            return
        self._callbacks.append(callback)

    def clear_callbacks(self):
        # type: () -> None
        self._callbacks = deque()

    def _execute_callback_queue(self):
        # type: () -> None
        """ execute callbacks and check if we defer this or not """
        if len(self._callbacks) == 0:
            return
        from protocol0 import Protocol0

        Protocol0.SELF.wait(0 if self._immediate else 1, self._execute_callbacks)

    def _execute_callbacks(self):
        # type: () -> None
        while len(self._callbacks):
            callback = self._callbacks.popleft()
            callback()

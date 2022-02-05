from collections import deque

from typing import Callable, Deque, Any

from protocol0.domain.enums.SongLoadStateEnum import SongLoadStateEnum
from protocol0.domain.shared.utils import get_callable_repr
from protocol0.infra.scheduler.Scheduler import Scheduler


class CallableWithCallbacks(object):
    def __init__(self, function):
        # type: (Callable) -> None
        super(CallableWithCallbacks, self).__init__()
        self._function = function  # type: Any
        self._callbacks = deque()  # type: Deque[Callable]

    def __repr__(self):
        # type: () -> str
        return "cwc %s" % get_callable_repr(self._function)

    def __call__(self, *a, **k):
        # type: (Any, Any) -> Any
        from protocol0.domain.lom.song.Song import Song

        if Song.get_instance().song_load_state == SongLoadStateEnum.LOADING and "listener" in str(self):
            return
        res = self._function(*a, **k)

        from protocol0.domain.sequence.Sequence import Sequence

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
        # defer mitigates the "Changes cannot be triggered by notification" error
        Scheduler.defer(self._execute_callbacks)

    def _execute_callbacks(self):
        # type: () -> None
        while len(self._callbacks):
            callback = self._callbacks.popleft()
            callback()

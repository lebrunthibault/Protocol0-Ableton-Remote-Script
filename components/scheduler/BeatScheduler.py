from typing import Callable, Any

from protocol0.components.scheduler.SyncedScheduler import SyncedScheduler
from protocol0.lom.AbstractObject import AbstractObject


class BeatScheduler(AbstractObject, SyncedScheduler):
    def __init__(self, exclusive=False, *a, **k):
        # type: (bool, Any, Any) -> None
        super(BeatScheduler, self).__init__(unschedule_on_stop=True, *a, **k)
        self._exclusive = exclusive

    def wait_bars(self, bar_length, callback):
        # type: (int, Callable) -> None
        """
        if exact if False, wait_bars executes the callback on the last beat preceding the next <bar_length> bar
        that is if the we are on the 3rd beat in 4/4, the callback will be executed in one beat
        This mode will work when global quantization is set to 1/4 or more
        """
        if not self.song.is_playing:
            return
        self.wait_beats(self.song.signature_numerator * bar_length, callback)

    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        if self._exclusive:
            self.clear()  # allow only one action at a time
        self.schedule_message(beats, callback)

    def clear(self):
        # type: () -> None
        # noinspection PyAttributeOutsideInit
        self._pending_action_list.clear()
        self._pending_precise_action_list.clear()

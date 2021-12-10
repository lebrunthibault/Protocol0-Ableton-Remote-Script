from functools import partial

from typing import Callable, Any

from protocol0.components.scheduler.SyncedScheduler import SyncedScheduler
from protocol0.lom.AbstractObject import AbstractObject


class BeatScheduler(AbstractObject, SyncedScheduler):
    TIMER_DELAY = 5  # mitigate not precise scheduling

    def __init__(self, exclusive=False, *a, **k):
        # type: (bool, Any, Any) -> None
        super(BeatScheduler, self).__init__(unschedule_on_stop=True, *a, **k)
        self._exclusive = exclusive

    def wait_bars(self, bar_length, callback, exact=False):
        # type: (int, Callable, bool) -> None
        """
        if exact if False, wait_bars executes the callback on the last beat preceding the next <bar_length> bar
        that is if the we are on the 3rd beat in 4/4, the callback will be executed in one beat
        This mode will work when global quantization is set to 1/4 or more
        """
        if not self.song.is_playing:
            return
        delay_shortening = 0 if exact else self.song.get_current_beats_song_time().beats
        beat_count = (self.song.signature_numerator * bar_length) - delay_shortening
        delay = 0 if exact else self.TIMER_DELAY
        self.parent.wait(delay, partial(self.wait_beats, beat_count, callback))

    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        if self._exclusive:
            self.clear()  # allow only one action at a time
        self.schedule_message("%d" % beats, callback)
        # self.schedule_message("%d" % floor(beats - 0.1), callback)

    def clear(self):
        # type: () -> None
        self._pending_action_lists = {}

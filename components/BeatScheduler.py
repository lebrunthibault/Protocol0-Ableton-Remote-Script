from functools import partial

from typing import Callable
from ClyphX_Pro.SyncedScheduler import SyncedScheduler
from a_protocol_0.lom.AbstractObject import AbstractObject


class BeatScheduler(AbstractObject, SyncedScheduler):
    TIMER_DELAY = 5  # mitigate not precise scheduling

    def __init__(self, *a, **k):
        SyncedScheduler.__init__(self, unschedule_on_stop=True, *a, **k)

    def wait_bars(self, bar_count, callback, exact=False):
        # type: (int, Callable, bool) -> None
        """
            if exact if False, wait_bars executes the callback on the last beat preceding the next <bar_count> bar
            that is if the we are on the 3rd beat in 4/4, the callback will be executed in one beat
            This mode will work when global quantization is set to 1/4 or more
        """
        beat_offset = 0 if exact else self.song.get_current_beats_song_time().beats
        beat_count = (self.song.signature_denominator * bar_count) - beat_offset
        delay = 0 if exact else self.TIMER_DELAY
        self.parent._wait(delay, partial(self.wait_beats, beat_count, callback))

    def wait_beats(self, beats, callback):
        # type: (int, Callable) -> None
        self.schedule_message("%d" % beats, callback)

    def clear(self):
        self._pending_action_lists = {}
        self.parent._wait(self.TIMER_DELAY + 1, partial(setattr, self, "_pending_action_lists", {}))

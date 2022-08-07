from functools import partial

from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.sequence.Sequence import Sequence


class AudioTailClip(AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        Scheduler.defer(partial(setattr, self.loop, "looping", False))

    def post_record(self, bar_length):
        # type: (int) -> None
        super(AudioTailClip, self).post_record(bar_length)
        if bar_length == 0:
            return None

        self.muted = True

    def fire(self):
        # type: () -> Optional[Sequence]
        self.muted = False
        seq = Sequence()

        seq.defer()  # wait for unmute
        seq.add(super(AudioTailClip, self).fire)
        seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)  # wait for the clip
        # start
        seq.wait_bars(self.loop.bar_length)
        seq.wait(5)
        seq.add(self._mute_if_stopped)

        return seq.done()

    def _mute_if_stopped(self):
        # type: () -> None
        if not self.is_playing:
            self.muted = True

from functools import partial

from typing import Any

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


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

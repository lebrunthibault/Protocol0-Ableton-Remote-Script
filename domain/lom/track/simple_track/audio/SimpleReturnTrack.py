from functools import partial

from typing import Any

from protocol0.domain.lom.track.TrackColorEnum import TrackColorEnum
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class SimpleReturnTrack(SimpleAudioTrack):
    IS_ACTIVE = False

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleReturnTrack, self).__init__(*a, **k)
        Scheduler.defer(
            partial(setattr, self.appearance, "color", TrackColorEnum.RETURN.value)
        )
        self.appearance.disconnect()

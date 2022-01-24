from functools import wraps

from typing import Any, TYPE_CHECKING

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.TrackDataEnum import TrackDataEnum
from protocol0.my_types import Func

if TYPE_CHECKING:
    from protocol0.lom.track.AbstractTrack import AbstractTrack


def save_track_data(func):
    # type: (Func) -> Func
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        res = func(*a, **k)
        from protocol0 import Protocol0
        Protocol0.SELF.trackDataManager.save(a[0])
        return res

    return decorate


class TrackDataManager(AbstractControlSurfaceComponent):
    def save(self, track):
        # type: (AbstractTrack) -> None
        from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack

        if isinstance(track, ExternalSynthTrack):
            track.set_data(TrackDataEnum.RECORD_CLIP_TAILS.name, track.record_clip_tails)

    def restore_data(self, track):
        # type: (AbstractTrack) -> None
        from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack

        if isinstance(track, ExternalSynthTrack) and track.audio_tail_track:
            track.record_clip_tails = track.get_data(TrackDataEnum.RECORD_CLIP_TAILS.name, track.instrument.RECORD_CLIP_TAILS)

    def clear(self):
        # type: () -> None
        for track in self.song.abstract_tracks:
            self.parent.log_notice("Clearing track data of %s" % track)

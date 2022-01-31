from typing import Any, TYPE_CHECKING

from protocol0.domain.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class TrackRoutingInterface(AbstractObject):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(TrackRoutingInterface, self).__init__(*a, **k)
        self._track = track._track

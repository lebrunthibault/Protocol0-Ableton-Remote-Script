from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack


class SimpleDummyTrackAddedEvent(object):
    def __init__(self, track):
        # type: (SimpleDummyTrack) -> None
        self.track = track

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack


class TrackDisconnectedEvent(object):
    def __init__(self, track):
        # type: (AbstractTrack) -> None
        self.track = track

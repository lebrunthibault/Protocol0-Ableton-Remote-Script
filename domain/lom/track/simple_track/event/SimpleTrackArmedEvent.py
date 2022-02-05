from typing import TYPE_CHECKING

from protocol0.domain.DomainEventInterface import DomainEventInterface

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleTrackArmedEvent(DomainEventInterface):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        self.track = track

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class TrackRoutingInterface(object):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        super(TrackRoutingInterface, self).__init__()
        # self.track = track
        self._track = track._track

    def __repr__(self):
        # type: () -> str
        return self.__class__.__name__

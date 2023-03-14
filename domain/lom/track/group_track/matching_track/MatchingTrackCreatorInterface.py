from typing import TYPE_CHECKING

from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent


class MatchingTrackCreatorInterface(object):
    def __init__(self, track_crud_component, base_track):
        # type: (TrackCrudComponent, SimpleTrack) -> None
        self._track_crud_component = track_crud_component
        self._base_track = base_track

    def bounce(self):
        # type: () -> Sequence
        raise NotImplementedError

from typing import TYPE_CHECKING, Any, List

from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractGroupTrack, self).__init__(track=base_group_track, *a, **k)
        base_group_track.abstract_group_track = self
        # for now: List[SimpleTrack] but AbstractGroupTracks will register themselves as seen just below
        self.sub_tracks = base_group_track.sub_tracks  # type: List[AbstractTrack]

        if base_group_track.group_track:
            self.group_track = base_group_track.group_track.abstract_group_track
            # creating the second layer relationship: abstract_group_tracks have List[AbstractTrack] as sub_tracks
            self.group_track.sub_tracks[self.group_track.sub_tracks.index(self.base_track)] = self

    @property
    def active_tracks(self):
        # type: () -> List[AbstractTrack]
        return self.sub_tracks

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip for track in self.sub_tracks for clip in track.clips]

from typing import TYPE_CHECKING, Any, List

from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractGroupTrack, self).__init__(track=group_track, *a, **k)
        # NB : here it is AbstractTrack because sub_tracks that are AbstractGroupTrack will register themselves as seen below
        self.sub_tracks = group_track.sub_tracks  # type: List[AbstractTrack]

        # attaching abstract_group_track to all direct children
        group_track.abstract_group_track = self
        group_track.abstract_track = self

        # creating the second relationship layer: abstract_group_tracks have List[AbstractTrack] as sub_tracks
        if self.group_track and self.base_track in self.group_track.abstract_group_track.sub_tracks:
            self.group_track.abstract_group_track.sub_tracks[
                self.group_track.abstract_group_track.sub_tracks.index(self.base_track)
            ] = self

        for sub_track in self.sub_tracks:
            sub_track.group_track = self

    @property
    def active_tracks(self):
        # type: () -> List[AbstractTrack]
        return self.sub_tracks

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip for track in self.sub_tracks for clip in track.clips]

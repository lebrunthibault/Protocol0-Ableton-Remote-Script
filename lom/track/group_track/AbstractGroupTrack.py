from typing import TYPE_CHECKING, Any, List

from protocol0.lom.clip.Clip import Clip
from protocol0.lom.track.AbstractTrack import AbstractTrack

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractGroupTrack, self).__init__(track=base_group_track, *a, **k)
        base_group_track.abstract_group_track = self
        # filled when link_sub_tracks is called
        self.sub_tracks = []  # type: List[AbstractTrack]
        # for now: List[SimpleTrack] but AbstractGroupTracks will register themselves as seen just below

    def link_parent_and_child_objects(self):
        # type: () -> None
        # only simple tracks non foldable at this point :
        # leave room for AbstractGroupTracks to register on the sub_tracks listN
        self.sub_tracks[:] = [sub_track for sub_track in self.base_track.sub_tracks if not sub_track.is_foldable]

        # point sub tracks to self
        for sub_track in self.sub_tracks:
            sub_track.group_track = self

        # connect to the enclosing group track is any
        if self.base_track.group_track:
            self.group_track = self.base_track.group_track.abstract_group_track
            # creating the second layer relationship: abstract_group_tracks have List[AbstractTrack] as sub_tracks
            if self.group_track:
                self.group_track.sub_tracks.append(self)
                self.group_track.sub_tracks.sort(key=lambda x: x.index)

    @property
    def active_tracks(self):
        # type: () -> List[AbstractTrack]
        return self.sub_tracks

    def is_parent(self, abstract_track):
        # type: (AbstractTrack) -> bool
        """ checks if the given track is not itself or a possibly nested child """
        return (
                abstract_track == self
                or abstract_track in self.sub_tracks
                or any(
            isinstance(sub_track, AbstractGroupTrack) and sub_track.is_parent(abstract_track)
            for sub_track in self.sub_tracks
        )
        )

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip for track in self.sub_tracks for clip in track.clips]

from typing import List, Optional, cast, Tuple

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyReturnTrack import \
    SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(AbstractGroupTrack, self).__init__(base_group_track)
        self.base_track.abstract_group_track = self
        # filled when link_sub_tracks is called
        self.group_track = self.group_track  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]
        # for now: List[SimpleTrack] but AbstractGroupTracks will register themselves on_tracks_change
        self.dummy_track = None  # type: Optional[SimpleDummyTrack]
        self.dummy_return_track = None  # type: Optional[SimpleDummyReturnTrack]

    def on_tracks_change(self):
        # type: () -> None
        self._link_sub_tracks()
        self._link_group_track()
        self._map_dummy_tracks()

    def _link_sub_tracks(self):
        # type: () -> None
        """ 2nd layer linking """
        # here we don't necessarily link the sub tracks to self
        self.sub_tracks[:] = self.base_track.sub_tracks

    def _link_sub_track(self, sub_track):
        # type: (SimpleTrack) -> None
        sub_track.group_track = self.base_track
        sub_track.abstract_group_track = self

    def _link_group_track(self):
        # type: () -> None
        """
            2nd layer linking
            Connect to the enclosing abg group track is any
        """
        if self.base_track.group_track is None:
            self.group_track = None
            return

        # NB : self.group_track is necessarily not None here because a foldable track always has an abg
        assert self.base_track.group_track.abstract_group_track
        self.group_track = self.base_track.group_track.abstract_group_track
        self.abstract_group_track = self  # because we already are the abstract group track
        self.group_track.add_or_replace_sub_track(self, self.base_track)

    def _map_dummy_tracks(self):
        # type: () -> None
        dummy_track, dummy_return_track = self._get_dummy_tracks()

        # no change
        if dummy_track == self.dummy_track and dummy_return_track == self.dummy_return_track:
            return None

        if dummy_track is not None:
            if dummy_track._track != getattr(self.dummy_track, "_track", None):
                self.dummy_track = SimpleDummyTrack(dummy_track._track, dummy_track.index)
                self.add_or_replace_sub_track(self.dummy_track, dummy_track)
                self._link_sub_track(self.dummy_track)
        else:
            if self.dummy_track is not None:
                self.dummy_track.disconnect()
                self.dummy_track = None

        if dummy_return_track is not None:
            if dummy_return_track._track != getattr(self.dummy_return_track, "_track", None):
                self.dummy_return_track = SimpleDummyReturnTrack(dummy_return_track._track,
                                                                 dummy_return_track.index)
                self.add_or_replace_sub_track(self.dummy_return_track, dummy_return_track)
                self._link_sub_track(self.dummy_return_track)
        else:
            if self.dummy_return_track is not None:
                self.dummy_return_track.disconnect()
                self.dummy_return_track = None

        Scheduler.wait(3, self._route_sub_tracks)

    def _get_dummy_tracks(self):
        # type: () -> Tuple[Optional[AbstractTrack], Optional[AbstractTrack]]
        if SimpleDummyTrack.is_track_valid(self.sub_tracks[-1]):
            if SimpleDummyTrack.is_track_valid(self.sub_tracks[-2]):
                return self.sub_tracks[-2], self.sub_tracks[-1]
            else:
                # is it the dummy return track ?
                if SimpleDummyReturnTrack.is_track_valid(self.sub_tracks[-1]):
                    return None, self.sub_tracks[-1]
                else:
                    return self.sub_tracks[-1], None

        return None, None

    def _route_sub_tracks(self):
        # type: () -> None
        simple_tracks = [track for track in self.sub_tracks if not isinstance(track, SimpleDummyTrack)]
        output_track = self.dummy_track if self.dummy_track is not None else self.base_track

        for track in simple_tracks:
            track.output_routing.track = cast(SimpleTrack, output_track)

    def is_parent(self, abstract_track):
        # type: (AbstractTrack) -> bool
        """ checks if the given track is not itself or a possibly nested child """
        return (
                abstract_track == self
                or abstract_track in self.sub_tracks
                or any(
            isinstance(sub_track, AbstractGroupTrack) and sub_track.is_parent(abstract_track)
            for sub_track in self.sub_tracks)
        )

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return self.base_track.clip_slots

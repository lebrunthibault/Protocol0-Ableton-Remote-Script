from typing import List, Optional, cast

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
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

    def on_tracks_change(self):
        # type: () -> None
        self._link_sub_tracks()
        self._link_group_track()
        self._map_dummy_track()

    def _link_sub_tracks(self):
        # type: () -> None
        """ 2nd layer linking """
        # here we don't necessarily link the sub tracks to self
        self.sub_tracks[:] = self.base_track.sub_tracks

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

    def _map_dummy_track(self):
        # type: () -> None
        dummy_audio_track = self._get_dummy_track()
        if getattr(dummy_audio_track, "_track", None) == getattr(self.dummy_track, "_track", None):
            return  # no change

        if dummy_audio_track:
            self.dummy_track = SimpleDummyTrack(dummy_audio_track._track, dummy_audio_track.index)
            self.add_or_replace_sub_track(self.dummy_track, dummy_audio_track)
            self.dummy_track.group_track = self.base_track
            self.dummy_track.abstract_group_track = self

        Scheduler.wait(3, self._route_sub_tracks)

    def _get_dummy_track(self):
        # type: () -> Optional[SimpleAudioTrack]
        if len(self.sub_tracks) == 1:
            return None

        track = self.sub_tracks[-1]
        if isinstance(track, SimpleAudioTrack) and not track.is_foldable and track.instrument is None:
            return track

        return None

    def _route_sub_tracks(self):
        # type: () -> None
        simple_tracks = [track for track in self.sub_tracks if track != self.dummy_track]
        output_track = self.dummy_track if self.dummy_track is not None else self.base_track

        for track in simple_tracks:
            if track.has_audio_output:
                track.output_routing.track = cast(SimpleTrack, output_track)

    def is_parent(self, abstract_track):
        # type: (AbstractTrack) -> bool
        """ checks if the given track is not itself or a possibly nested child """
        return (
                abstract_track == self
                or abstract_track in self.sub_tracks
                or any(isinstance(sub_track, AbstractGroupTrack) and sub_track.is_parent(abstract_track)
                       for sub_track in self.sub_tracks)
        )

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        return self.base_track.clip_slots

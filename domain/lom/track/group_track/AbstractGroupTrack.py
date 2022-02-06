from typing import TYPE_CHECKING, Any, List, Optional, Iterator

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.infra.scheduler.Scheduler import Scheduler

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractGroupTrack, self).__init__(track=base_group_track, *a, **k)
        self.base_track.abstract_group_track = self
        base_group_track.track_name.disconnect()
        # filled when link_sub_tracks is called
        self.group_track = self.group_track  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]
        # for now: List[SimpleTrack] but AbstractGroupTracks will register themselves on_tracks_change
        self.dummy_tracks = []  # type: List[SimpleDummyTrack]

    def on_tracks_change(self):
        # type: () -> None
        self._link_sub_tracks()
        self._link_group_track()
        self._map_dummy_tracks()

    def _link_sub_tracks(self):
        # type: () -> None
        """ 2nd layer linking """
        update_name = len(self.sub_tracks) != len(self.base_track.sub_tracks)
        self.sub_tracks[:] = self.base_track.sub_tracks
        # here we don't necessarily link the sub tracks to self
        if update_name:
            Scheduler.defer(self.track_name.update)

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
        self.abstract_group_track = self.base_track.group_track.abstract_group_track
        self.append_to_sub_tracks(self.group_track, self, self.base_track)

    def _get_dummy_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        dummy_tracks = []
        for track in reversed(self.sub_tracks):
            if isinstance(track, SimpleAudioTrack) and not track.is_foldable and track.instrument is None:
                dummy_tracks.append(track)

            # checks automated tracks are all the same type to avoid triggering on wrong track layouts
            main_tracks = self.sub_tracks[:self.sub_tracks.index(track)]
            if len(main_tracks) == 0 or not all([isinstance(track, main_tracks[0].__class__) for track in main_tracks]):
                return iter([])

        return reversed(dummy_tracks)

    def _map_dummy_tracks(self):
        # type: () -> None
        dummy_tracks = list(self._get_dummy_tracks())
        if len(self.dummy_tracks) == len(dummy_tracks):
            return

        from protocol0 import Protocol0

        self.dummy_tracks[:] = [
            Protocol0.SELF.songTracksManager.generate_simple_track(track=track._track, index=track.index,
                                                                   cls=SimpleDummyTrack)
            for track in dummy_tracks]
        for dummy_track in self.dummy_tracks:
            dummy_track.abstract_group_track = self
            Scheduler.defer(dummy_track.track_name.update)

        Scheduler.wait(3, self._link_dummy_tracks_routings)

    def _link_dummy_tracks_routings(self):
        # type: () -> None
        simple_tracks = [track for track in self.sub_tracks if track not in self.dummy_tracks]
        if len(self.dummy_tracks) == 0:
            for track in simple_tracks:
                if track.has_audio_output:
                    track.output_routing.track = self.base_track
            return

        dummy_track = self.dummy_tracks[0]
        for track in simple_tracks:
            if track.has_audio_output:
                track.output_routing.track = dummy_track
        for next_dummy_track in self.dummy_tracks[1:]:
            dummy_track.output_routing.track = next_dummy_track
            dummy_track = next_dummy_track
        dummy_track.output_routing.track = self.base_track

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
                or any(isinstance(sub_track, AbstractGroupTrack) and sub_track.is_parent(abstract_track)
                       for sub_track in self.sub_tracks)
        )

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip for track in self.sub_tracks for clip in track.clips]

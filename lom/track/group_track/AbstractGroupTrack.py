from typing import TYPE_CHECKING, Any, List, Iterator

from protocol0.lom.clip.Clip import Clip
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractGroupTrack(AbstractTrack):
    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(AbstractGroupTrack, self).__init__(track=base_group_track, *a, **k)
        base_group_track.abstract_group_track = self
        # filled when link_sub_tracks is called
        self.sub_tracks = []  # type: List[AbstractTrack]
        self.dummy_tracks = []  # type: List[SimpleDummyTrack]
        # for now: List[SimpleTrack] but AbstractGroupTracks will register themselves in post_init

    def post_init(self):
        # type: () -> None
        self._link_group_track_and_subtracks()
        self._map_dummy_tracks()

    def _link_group_track_and_subtracks(self):
        # type: () -> None
        """
            NB : out of init because this needs to be done every rebuild
            2nd layer linking
        """
        # only simple tracks non foldable at this point :
        # leave room for AbstractGroupTracks to register on the sub_tracks list
        self.sub_tracks[:] = self.base_track.sub_tracks

        # connect to the enclosing group track is any
        if self.base_track.group_track:
            self.group_track = self.base_track.group_track.abstract_group_track
            # creating the second layer relationship: abstract_group_tracks have List[AbstractTrack] as sub_tracks
            if self.group_track:
                self.group_track.sub_tracks.append(self)
                if self.base_track in self.group_track.sub_tracks:
                    self.group_track.sub_tracks.remove(self.base_track)
                    # this is because we add first the dummy tracks and then previous abg register themselves
                    self.group_track.sub_tracks.sort(key=lambda x: x.index)

    def _get_dummy_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        for track in reversed(self.sub_tracks):
            if isinstance(track, SimpleAudioTrack) and not track.is_foldable and track.instrument is None:
                yield track
            return

    def _map_dummy_tracks(self):
        # type: () -> None
        dummy_tracks = list(self._get_dummy_tracks())
        if len(self.dummy_tracks) == len(dummy_tracks):
            return

        self.dummy_tracks[:] = [self.parent.songManager.generate_simple_track(track=track._track, cls=SimpleDummyTrack)
                                for track in dummy_tracks]

        self.parent.defer(self._link_dummy_tracks_routings)

    def _link_dummy_tracks_routings(self):
        # type: () -> None
        simple_tracks = [track for track in self.sub_tracks if track not in self.dummy_tracks]
        if len(self.dummy_tracks) == 0:
            for track in simple_tracks:
                if track.has_audio_output:
                    track.output_routing_track = self.base_track
            return

        dummy_track = self.dummy_tracks[0]
        for track in simple_tracks:
            if track.has_audio_output:
                track.output_routing_track = dummy_track
        for next_dummy_track in self.dummy_tracks[1:]:
            dummy_track.output_routing_track = next_dummy_track
            dummy_track = next_dummy_track
        dummy_track.output_routing_track = self.base_track

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

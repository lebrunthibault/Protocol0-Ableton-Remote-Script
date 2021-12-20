import collections

from typing import Any, Optional, Type, Dict, Iterator

import Live
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.SongLoadStateEnum import SongLoadStateEnum
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.lom.track.simple_track.SimpleMasterTrack import SimpleMasterTrack
from protocol0.lom.track.simple_track.SimpleReturnTrack import SimpleReturnTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import handle_error, p0_subject_slot


class SongTracksManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SongTracksManager, self).__init__(*a, **k)

        self._live_track_id_to_simple_track = collections.OrderedDict()  # type: Dict[int, SimpleTrack]
        self.tracks_listener.subject = self.song._song

    @property
    def live_tracks(self):
        # type: () -> Iterator[Live.Track.Track]
        return (track for track in list(self._song.tracks) + list(self._song.return_tracks) + [self._song.master_track])

    def get_simple_track(self, live_track):
        # type: (Live.Track.Track) -> SimpleTrack
        """ we use the live ptr instead of the track to be able to access outdated simple tracks on deletion """
        return self._live_track_id_to_simple_track[live_track._live_ptr]

    def get_optional_simple_track(self, live_track):
        # type: (Live.Track.Track) -> Optional[SimpleTrack]
        try:
            return self.get_simple_track(live_track)
        except KeyError:
            return None

    def add_simple_track(self, simple_track):
        # type: (SimpleTrack) -> None
        self._live_track_id_to_simple_track[simple_track.live_id] = simple_track

    @property
    def all_simple_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        return (track for track in self._live_track_id_to_simple_track.values())

    @p0_subject_slot("tracks")
    @handle_error
    def tracks_listener(self):
        # type: () -> Sequence
        self._clean_deleted_tracks()

        previous_simple_track_count = len(list(self.all_simple_tracks))
        has_added_tracks = 0 < previous_simple_track_count < len(list(self.live_tracks))

        self._generate_simple_tracks()
        self._generate_abstract_group_tracks()

        self.parent.log_info("mapped tracks")

        seq = Sequence()
        if has_added_tracks and self.song.selected_track:
            seq.add(self.parent.trackManager.on_added_track)

        return seq.done()

    def _clean_deleted_tracks(self):
        # type: () -> None
        existing_track_ids = [track._live_ptr for track in self.live_tracks]
        deleted_ids = []

        for track_id, simple_track in self._live_track_id_to_simple_track.items():
            if track_id not in existing_track_ids:
                simple_track.disconnect()
                if simple_track.abstract_group_track:
                    simple_track.abstract_group_track.disconnect()
                deleted_ids.append(track_id)

        for track_id in deleted_ids:
            del self._live_track_id_to_simple_track[track_id]

    def _generate_simple_tracks(self):
        # type: () -> None
        """ instantiate SimpleTracks (including return / master, that are marked as inactive) """
        self.song.usamo_track = None
        self.template_dummy_clip = None  # type: Optional[AudioClip]

        # instantiate set tracks
        for index, track in enumerate(list(self.song._song.tracks)):
            self.generate_simple_track(track=track, index=index)

        if self.song.usamo_track is None and self.song.song_load_state != SongLoadStateEnum.LOADED:
            self.parent.log_warning("Usamo track is not present")

        for index, track in enumerate(list(self.song._song.return_tracks)):
            self.generate_simple_track(track=track, index=index, cls=SimpleReturnTrack)

        self.song.master_track = self.generate_simple_track(track=self.song._song.master_track, index=0, cls=SimpleMasterTrack)

        self._sort_simple_tracks()

        for scene in self.song.scenes:
            scene.on_tracks_change()

    def generate_simple_track(self, track, index, cls=None):
        # type: (Live.Track.Track, int, Optional[Type[SimpleTrack]]) -> SimpleTrack
        simple_track = self.parent.trackManager.instantiate_simple_track(track=track, index=index, cls=cls)
        self._register_simple_track(simple_track)
        if index is not None:
            simple_track._index = index
        simple_track.on_tracks_change()

        if self.song.usamo_track is None:
            if simple_track.get_device_from_enum(DeviceEnum.USAMO):
                self.song.usamo_track = simple_track

        if simple_track.name == SimpleInstrumentBusTrack.DEFAULT_NAME and len(simple_track.clips):
            self.song.template_dummy_clip = simple_track.clips[0]

        return simple_track

    def _register_simple_track(self, simple_track):
        # type: (SimpleTrack) -> None
        # rebuild sub_tracks
        simple_track.sub_tracks = []

        # handling replacement of a SimpleTrack by another
        previous_simple_track = self.get_optional_simple_track(simple_track._track)
        if previous_simple_track and previous_simple_track != simple_track:
            self._replace_simple_track(previous_simple_track, simple_track)

        self.add_simple_track(simple_track)

    def _replace_simple_track(self, previous_simple_track, new_simple_track):
        # type: (SimpleTrack, SimpleTrack) -> None
        """ disconnecting and removing from SimpleTrack group track and abstract_group_track """
        new_simple_track._index = previous_simple_track._index
        previous_simple_track.disconnect()
        append_to_sub = self.parent.trackManager.append_to_sub_tracks

        if previous_simple_track.group_track:
            append_to_sub(previous_simple_track.group_track, new_simple_track, previous_simple_track)

        if previous_simple_track.abstract_group_track:
            append_to_sub(previous_simple_track.abstract_group_track, new_simple_track, previous_simple_track)

    def _sort_simple_tracks(self):
        # type: () -> None
        sorted_dict = collections.OrderedDict()
        for track in self.live_tracks:
            sorted_dict[track._live_ptr] = self.get_simple_track(track)
        self._live_track_id_to_simple_track = sorted_dict

    def _generate_abstract_group_tracks(self):
        # type: () -> None
        # 2nd pass : instantiate AbstractGroupTracks
        for track in self.song.simple_tracks:
            if track.is_foldable:
                self.parent.trackManager.instantiate_abstract_group_track(track)

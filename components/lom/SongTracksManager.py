from typing import Any, Optional, Type

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
        self.tracks_listener.subject = self.song._song

    @p0_subject_slot("tracks")
    @handle_error
    def tracks_listener(self, purge=False):
        # type: (bool) -> Optional[Sequence]
        # Check if tracks were added

        self.parent.log_dev(type(self.song.live_track_to_simple_track))
        self.parent.log_dev(len(list(self.song.live_track_to_simple_track)))
        self.parent.log_dev(self.song.live_track_to_simple_track.values())
        if purge:
            self.parent.songManager.purge()

        previous_simple_track_count = len(list(self.song.all_simple_tracks))
        has_added_tracks = 0 < previous_simple_track_count < len(self.song._song.tracks)

        self._generate_simple_tracks()
        self._generate_abstract_group_tracks()

        self.parent.log_info("mapped tracks")

        if has_added_tracks and self.song.selected_track:
            seq = Sequence()
            seq.add(self.parent.trackManager.on_added_track)
            return seq.done()

    def _generate_simple_tracks(self):
        # type: () -> None
        """ instantiate SimpleTracks (including return / master, that are marked as inactive) """
        self.song.usamo_track = None
        self.template_dummy_clip = None  # type: Optional[AudioClip]

        # instantiate set tracks
        for track in list(self.song._song.tracks):
            self.generate_simple_track(track=track)

        for track in list(self.song._song.return_tracks):
            self.generate_simple_track(track=track, cls=SimpleReturnTrack)

        self.song.master_track = self.generate_simple_track(track=self.song._song.master_track, cls=SimpleMasterTrack)

        if self.song.usamo_track is None and self.song.song_load_state != SongLoadStateEnum.LOADED:
            self.parent.log_warning("Usamo track is not present")

        # Refresh track mapping
        # self.parent.log_dev(self.song.live_track_to_simple_track)
        # for track in self.song.live_track_to_simple_track.keys():
        #     if track not in self.song.live_tracks:
        #         track.disconnect()

    def generate_simple_track(self, track, cls=None):
        # type: (Live.Track.Track, Optional[Type[SimpleTrack]]) -> SimpleTrack
        simple_track = self.parent.trackManager.instantiate_simple_track(track=track, cls=cls)
        self._register_simple_track(simple_track)
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
        if simple_track._track in self.song.live_track_to_simple_track:
            previous_simple_track = self.song.live_track_to_simple_track[simple_track._track]
            if previous_simple_track != simple_track:
                self._replace_simple_track(previous_simple_track, simple_track)
        # else:
        #     # normal registering
        #     self._simple_tracks.append(simple_track)

        self.song.live_track_to_simple_track[simple_track._track] = simple_track

    def _replace_simple_track(self, previous_simple_track, new_simple_track):
        # type: (SimpleTrack, SimpleTrack) -> None
        """ disconnecting and removing from SimpleTrack group track and abstract_group_track """
        previous_simple_track.disconnect()
        append_to_sub = self.parent.trackManager.append_to_sub_tracks

        if previous_simple_track.group_track:
            append_to_sub(previous_simple_track.group_track, new_simple_track, previous_simple_track)

        if previous_simple_track.abstract_group_track:
            append_to_sub(previous_simple_track.abstract_group_track, new_simple_track, previous_simple_track)

    def _generate_abstract_group_tracks(self):
        # type: () -> None
        # 2nd pass : instantiate AbstractGroupTracks
        for track in self.song.simple_tracks:
            if track.is_foldable:
                self.parent.trackManager.instantiate_abstract_group_track(track)

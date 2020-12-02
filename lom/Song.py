from typing import Any, Optional, List

from a_protocol_0.consts import GROUP_EXT_NAMES, TRACK_CATEGORIES, TRACK_CATEGORY_ALL
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.SongActionMixin import SongActionMixin
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.GroupTrack import GroupTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class Song(SongActionMixin, AbstractObject):
    def __init__(self, *a, **k):
        super(Song, self).__init__(song=self, *a, **k)
        self._song = self.parent.song()
        self.parent.song = self
        self.view = self._song.view  # type: Any
        self.tracks = []  # type: List[SimpleTrack]
        self.g_tracks = []  # type: List[GroupTrack]
        self.parent.defer(self.build_tracks)
        self.tracks_added = False
        self.selected_track_category = TRACK_CATEGORIES[0]

    def init_listeners(self):
        # type: () -> None
        self._song.add_tracks_listener(self.build_tracks)

    def build_tracks(self):
        """ do it one at at a time to be able to access tracks during instantiation"""
        if len(self._song.tracks) > len(self.tracks):
            self.tracks_added = True
        self.tracks = []
        self.g_tracks = []
        [self.tracks.append(SimpleTrack(track=track, index=i)) for i, track in enumerate(list(self._song.tracks))]
        [self.g_tracks.append(GroupTrack(base_track=track)) for track in self.tracks if track.name in GROUP_EXT_NAMES]
        self.parent.log("Song : built tracks")
        self.parent.sessionManager._setup_session_control()

    @property
    def scenes(self):
        # type: () -> List[Any]
        return self._song.scenes

    @property
    def selected_track(self):
        # type: () -> Optional[SimpleTrack]
        if not self.view.selected_track:
            return None

        return self._get_track(self.view.selected_track)

    @selected_track.setter
    def selected_track(self, selected_track):
        # type: (SimpleTrack) -> None
        self.view.selected_track = selected_track._track

    @property
    def current_track(self):
        # type: () -> Optional[AbstractTrack]
        return self.selected_track.g_track if self.selected_track.is_groupable else self.selected_track

    @property
    def visible_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.is_visible]

    @property
    def top_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.is_top_visible]

    @property
    def simple_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if not track.is_groupable]

    @property
    def group_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.is_simple_group]

    @property
    def solo_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.solo]

    @property
    def selected_category_tracks(self):
        # type: () -> List[SimpleTrack]
        if self.selected_track_category == TRACK_CATEGORY_ALL:
            return self.tracks
        return [track for track in self.tracks if track.category.lower() == self.selected_track_category.lower()]

    @property
    def group_tracks_names(self):
        # type: () -> List[str]
        return [track.name for track in self.tracks if track.is_simple_group]

    @property
    def playing_tracks(self):
        # type: () -> List[AbstractTrack]
        return [track for track in self.tracks if track.is_playing]

    def _get_track(self, track):
        # type: (Any) -> SimpleTrack
        if isinstance(track, AbstractTrack):
            raise Exception("Expected Live track, got AbstractTrack instead")

        for t in self.tracks:
            if t._track == track:
                return t

        raise Exception("this track cannot be matched")

    @property
    def session_track_offset(self):
        # type: () -> int
        return self.song.visible_tracks.index(self.current_track.base_track)

    @property
    def tempo(self):
        # type: () -> float
        return self._song.tempo

    @property
    def metronome(self):
        # type: () -> float
        return self._song.metronome

    @metronome.setter
    def metronome(self, metronome):
        # type: (bool) -> None
        self._song.metronome = metronome

    @property
    def is_playing(self):
        # type: () -> float
        return self._song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        self._song.is_playing = is_playing

    @property
    def session_record_status(self):
        # type: () -> float
        return self._song.session_record_status

    @property
    def clip_trigger_quantization(self):
        # type: () -> int
        return self._song.clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, clip_trigger_quantization):
        # type: (int) -> None
        self._song.clip_trigger_quantization = clip_trigger_quantization

    def bar_count_length(self, bar_count):
        # type: (int) -> int
        return round((600 / self.tempo) * (4 * int(bar_count) - 0.5))

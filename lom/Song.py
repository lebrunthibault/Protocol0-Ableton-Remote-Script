from typing import Any, Optional, List

from a_protocol_0.consts import TRACK_CATEGORIES, TRACK_CATEGORY_ALL
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.SongActionMixin import SongActionMixin
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class Song(SongActionMixin, AbstractObject):
    def __init__(self, song=None, *a, **k):
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Any
        self.tracks = []  # type: List[SimpleTrack]
        self.group_tracks = []  # type: List[SimpleTrack]
        self.selected_track = None  # type: Optional[SimpleTrack]
        self.current_track = None  # type: Optional[AbstractTrack]
        self.tracks_added = False
        self.selected_track_category = TRACK_CATEGORIES[0]

    @property
    def scenes(self):
        # type: () -> List[Any]
        return self._song.scenes

    @property
    def visible_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.is_visible]

    @property
    def top_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.is_visible and not track.is_external_synth_sub_track]

    @property
    def solo_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.solo]

    @property
    def playing_tracks(self):
        # type: () -> List[AbstractTrack]
        return [track for track in self.tracks if track.is_playing]

    @property
    def selected_category_tracks(self):
        # type: () -> List[SimpleTrack]
        if self.selected_track_category == TRACK_CATEGORY_ALL:
            return self.tracks
        return [track for track in self.tracks if track.category.lower() == self.selected_track_category.lower()]

    @property
    def is_playing(self):
        # type: () -> float
        return self._song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        self._song.is_playing = is_playing

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

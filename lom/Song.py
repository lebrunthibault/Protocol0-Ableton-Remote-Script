from typing import Any, List, Optional

import Live

from _Framework.Util import find_if
from a_protocol_0.consts import TRACK_CATEGORY_ALL
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.SongActionMixin import SongActionMixin
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class Song(SongActionMixin, AbstractObject):
    def __init__(self, song, *a, **k):
        # type: (Live.Song.Song) -> None
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Any
        self.tracks = []  # type: List[SimpleTrack]
        self.abstract_tracks = []  # type: List[AbstractTrack]
        self.abstract_group_tracks = []  # type: List[AbstractGroupTrack]
        self.selected_track = None  # type: SimpleTrack
        self.current_track = None  # type: AbstractTrack
        self.master_track = self._song.master_track  # type: Live.Track.Track
        self.clip_slots = []  # type: List[ClipSlot]
        self.selected_track_category = TRACK_CATEGORY_ALL
        self.selected_recording_time = "4 bars"

    def __call__(self):
        # type: () -> Live.Song.Song
        """ allows for self.song() behavior to extend other surface script classes """
        return self.parent.song()

    @property
    def scenes(self):
        # type: () -> List[Any]
        return self._song.scenes

    def next_track(self, increment=1):
        # type: (int) -> SimpleTrack
        return self.tracks[(self.selected_track.index + increment) % len(self.tracks)]

    @property
    def scrollable_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.is_visible and track.is_scrollable]

    @property
    def root_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if not track.group_track]

    @property
    def selected_tracks(self):
        # type: () -> List[AbstractTrack]
        return [self.parent.songManager.get_current_track(track) for track in self.tracks if track._track.is_part_of_selection]

    @property
    def selected_category_tracks(self):
        # type: () -> List[SimpleTrack]
        if self.selected_track_category == TRACK_CATEGORY_ALL:
            return self.tracks
        return [track for track in self.tracks if track.category.lower() == self.selected_track_category.lower()]

    @property
    def highlighted_clip_slot(self):
        # type: () -> Optional[ClipSlot]
        """ first look in track then in song """
        return find_if(lambda cs: cs._clip_slot == self.song._view.highlighted_clip_slot,
                       self.selected_track.clip_slots) or find_if(
            lambda cs: cs._clip_slot == self.song._view.highlighted_clip_slot, [cs for track in self.song.tracks for cs in track.clip_slots])

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> None
        self.song._view.highlighted_clip_slot = clip_slot._clip_slot

    @property
    def is_playing(self):
        return self._song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        self._song.is_playing = is_playing

    @property
    def metronome(self):
        # type: () -> float
        return self._song.metronome

    @metronome.setter
    def metronome(self, metronome):
        # type: (bool) -> None
        self._song.metronome = metronome

    @property
    def clip_trigger_quantization(self):
        # type: () -> int
        return self._song.clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, clip_trigger_quantization):
        # type: (int) -> None
        self._song.clip_trigger_quantization = clip_trigger_quantization

    @property
    def playing_clips(self):
        # type: () -> List[Clip]
        return [t.playable_clip for t in self.tracks if t.is_playing and t.playable_clip.is_playing]
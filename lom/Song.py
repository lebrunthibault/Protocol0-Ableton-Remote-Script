from typing import Any, List, Optional

import Live
from _Framework.Util import find_if
from a_protocol_0.consts import TRACK_CATEGORY_ALL
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.SongActionMixin import SongActionMixin
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class Song(SongActionMixin, AbstractObject):
    def __init__(self, song, *a, **k):
        # type: (Live.Song.Song) -> None
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Any
        self.tracks = []  # type: List[SimpleTrack]
        self.external_synth_tracks = []  # type: List[ExternalSynthTrack]
        self.selected_track = None  # type: SimpleTrack
        self.current_track = None  # type: AbstractTrack
        self.clip_slots = []  # type: List[ClipSlot]
        self.selected_track_category = TRACK_CATEGORY_ALL
        self.selected_recording_time = "4 bars"

    @property
    def scenes(self):
        # type: () -> List[Any]
        return self._song.scenes

    def next_track(self, increment=1):
        # type: (int) -> SimpleTrack
        return self.tracks[(self.selected_track.index + increment) % len(self.tracks)]

    @property
    def top_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.tracks if track.is_visible and not track.is_external_synth_sub_track]

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
            lambda cs: cs._clip_slot == self.song._view.highlighted_clip_slot, self.song.clip_slots)

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> None
        self.song._view.highlighted_clip_slot = clip_slot._clip_slot

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

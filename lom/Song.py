from typing import Any, Optional

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


class Song:
    def __init__(self, song):
        # type: (Any) -> None
        self._song = song
        self.tracks = [SimpleTrack(self, track, i + 1) for i, track in
                       enumerate(list(song.tracks))]  # type: list[SimpleTrack]
        for track in self.tracks:
            track.song = self

    @property
    def tempo(self):
        # type: () -> float
        return self._song.tempo

    @property
    def view(self):
        # type: () -> Any
        return self._song.view

    @property
    def top_tracks(self):
        # type: () -> list[SimpleTrack]
        return [track for track in self.tracks if track.is_top_visible]

    @property
    def simple_tracks(self):
        # type: () -> list[SimpleTrack]
        return [track for track in self.tracks if not track.is_groupable]

    def simple_armed_tracks(self, track):
        # type: (AbstractTrack) -> list[SimpleTrack]
        return [t for t in self.simple_tracks if t.is_armed and t != track]

    @property
    def group_ex_tracks(self):
        # type: () -> list[GroupTrack]
        return [GroupTrack(self, track.track) for track in self.tracks if
                track.name.is_group_track]

    @property
    def selected_track(self):
        # type: () -> Optional[SimpleTrack]
        if not self.view.selected_track:
            return None

        return self.get_track(self.view.selected_track)

    @property
    def clip_trigger_quantization(self):
        # type: () -> int
        return self._song.clip_trigger_quantization + 1

    def playing_clips_count(self, abstract_track):
        # type: (AbstractTrack) -> int
        """ number of playing clip count in the live set excluding the group track """
        playing_clips_count = len([clip_slot for track in self.tracks for clip_slot in track.clip_slots
                                   if track.index != abstract_track.index
                                   and clip_slot.clip
                                   and not clip_slot.clip.name.startswith("[]")
                                   and clip_slot.clip.is_playing])

        return playing_clips_count

    def has_set_playing_clips(self, abstract_track):
        # type: (AbstractTrack) -> bool
        """ find if there is playing clips elsewhere
            by default checks also in group track
        """
        return self.playing_clips_count(abstract_track) != 0

    def delay_before_recording_end(self, bar_count):
        # type: (int) -> int
        return int(round((600 / self._song.tempo) * (4 * (int(bar_count) + 1) - 0.5)))

    def get_track(self, track):
        # type: (Any) -> SimpleTrack
        for t in self.tracks:
            if t.track == track:
                return t

        raise Exception("this track cannot be matched")

    def other_armed_group_track(self, abstract_track=None):
        # type: (Optional[AbstractTrack]) -> Optional[GroupTrack]
        return next(iter([g_track for g_track in self.group_ex_tracks if (
                not abstract_track or not abstract_track.is_group_track or abstract_track.index != g_track.index) and g_track.any_armed]),
                    None)

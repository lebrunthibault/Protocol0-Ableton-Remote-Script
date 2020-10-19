from typing import Any

from ClyphX_Pro.clyphx_pro.user_actions._Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions._AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions._SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions._TrackName import TrackName


class GroupTrack(AbstractTrack):
    def __init__(self, song, base_track):
        # type: ("Song", Any) -> None
        # getting our track object
        track = song.get_track(base_track)
        self.track_index_group = track.index - 1

        # check if we clicked on group track instead of clyphx track
        if track.is_clyphx:
            self.track_index_group -= 1

        if track.index >= 3 and song.tracks[track.index - 2].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 2
        if track.index >= 4 and song.tracks[track.index - 3].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 3

        if self.track_index_group < 0 or self.track_index_group > len(song.tracks) - 2:
            raise Exception(
                "tried to instantiate group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                        self.track_index_group))
        self.clyphx.g_track = self.midi.g_track = self.audio.g_track = self

        super(GroupTrack, self).__init__(song, self.group.track, self.track_index_group)

    @property
    def index(self):
        # type: () -> int
        return self.group.index

    @property
    def track(self):
        # type: () -> int
        return self.group.track

    @property
    def scene_count(self):
        return self.audio.scene_count

    @property
    def first_empty_slot_index(self):
        return self.audio.first_empty_slot_index

    @property
    def name(self):
        # type: () -> str
        return self.group.name

    @property
    def is_foldable(self):
        # type: () -> bool
        return True

    @property
    def is_folded(self):
        # type: () -> bool
        return self.group.track.is_folded

    @property
    def is_group(self):
        # type: () -> bool
        return True

    @property
    def is_prophet(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_PROPHET_NAME

    @property
    def is_minitaur(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_MINITAUR_NAME

    @property
    def selectable_track(self):
        # type: () -> SimpleTrack
        return self.midi if self.is_prophet else self.audio

    @property
    def is_visible(self):
        # type: () -> bool
        return True

    @property
    def is_top_visible(self):
        # type: () -> bool
        return True

    @property
    def rec_clip_index(self):
        # type: () -> int
        return self.audio.rec_clip_index

    @property
    def has_empty_slot(self):
        # type: () -> int
        return self.audio.has_empty_slot

    @property
    def group(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group]

    @property
    def clyphx(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 1]

    @property
    def midi(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 2]

    @property
    def audio(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 3]

    @property
    def is_armed(self):
        # type: () -> bool
        return self.midi.is_armed and self.audio.is_armed

    @property
    def any_armed(self):
        # type: () -> bool
        return self.clyphx.is_armed or self.midi.is_armed or self.audio.is_armed

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def color(self):
        # type: () -> str
        if "Prophet" in self.group.name:
            return Colors.PROPHET
        elif "BS" in self.group.name:
            return Colors.BASS_STATION
        return Colors.DISABLED

    @property
    def beat_count_before_clip_restart(self):
        # type: () -> int
        if self.audio.beat_count_before_clip_restart:
            return self.audio.beat_count_before_clip_restart
        else:
            return self.midi.beat_count_before_clip_restart

from typing import Any, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.mixins.GroupTrackActionMixin import GroupTrackActionMixin
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument
from ClyphX_Pro.clyphx_pro.user_actions.lom.ClipSlot import ClipSlot
from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


class GroupTrack(GroupTrackActionMixin, AbstractTrack):
    def __init__(self, song, base_track):
        # type: ("Song", Any) -> None
        # getting our track object
        track = song.get_track(base_track)
        self.song = song  # type: Song
        self.track_index_group = track.index  # type: int

        # check if we clicked on group track instead of clyphx track
        if track.is_clyphx:
            self.track_index_group -= 1
        elif track.index >= 2 and song.tracks[track.index - 1].is_clyphx:
            self.track_index_group -= 2
        elif track.index >= 3 and song.tracks[track.index - 2].is_clyphx:
            self.track_index_group -= 3

        if song.tracks[self.track_index_group].is_group_ext:
            raise Exception(
                "tried to instantiate group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                        self.track_index_group))
        super(GroupTrack, self).__init__(song, self.group.track, self.track_index_group)

        self.clyphx.g_track = self.midi.g_track = self.audio.g_track = self

        # we need the group track name to be immutable as it's used to identify group tracks
        if not self.group._track.name_has_listener(self.group.name_listener):
            self.group._track.add_name_listener(self.group.name_listener)

    @property
    def track(self):
        # type: () -> int
        return self.group.track

    @property
    def instrument(self):
        # type: () -> AbstractInstrument
        return self.selectable_track.instrument

    @property
    def index(self):
        # type: () -> int
        return self.group.index

    @property
    def next_empty_clip_slot(self):
        # type: () -> ClipSlot
        return self.audio.next_empty_clip_slot

    @property
    def is_foldable(self):
        # type: () -> bool
        return True

    @property
    def is_folded(self):
        # type: () -> bool
        return self.group.track.is_folded

    @property
    def is_prophet_group_track(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_PROPHET_NAME

    @property
    def is_minitaur_group_track(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_MINITAUR_NAME

    @property
    def selectable_track(self):
        # type: () -> SimpleTrack
        return self.midi if self.is_prophet_group_track else self.audio

    @property
    def is_visible(self):
        # type: () -> bool
        return True

    @property
    def is_top_visible(self):
        # type: () -> bool
        return True

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
    def arm(self):
        # type: () -> bool
        return self.midi.arm and self.audio.arm

    @property
    def any_armed(self):
        # type: () -> bool
        return self.clyphx.arm or self.midi.arm or self.audio.arm

    @property
    def can_be_armed(self):
        # type: () -> bool
        return True

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.midi.is_recording or self.audio.is_recording

    @property
    def color(self):
        # type: () -> str
        if self.is_prophet_group_track:
            return Colors.PROPHET
        elif self.is_minitaur_group_track:
            return Colors.MINITAUR
        return Colors.DISABLED

    @color.setter
    def color(self, color):
        # type: (int) -> None
        self.clyphx.clips[0].color = color


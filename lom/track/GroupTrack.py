from typing import TYPE_CHECKING

from a_protocol_0.actions.mixins.GroupTrackActionMixin import GroupTrackActionMixin
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    from a_protocol_0.lom.Song import Song


class GroupTrack(GroupTrackActionMixin, AbstractTrack):
    def __init__(self, song, base_track):
        # type: ("Song", SimpleTrack) -> None
        # getting our track object
        self.song = song  # type: Song
        self.track_index_group = base_track.index  # type: int

        if not base_track.is_groupable:
            raise Exception(
                "tried to instantiate non group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                            self.track_index_group))
        # check if selectable track is part of group
        if song.tracks[base_track.index - 1].is_group_ext:
            self.track_index_group -= 1
        elif song.tracks[base_track.index - 2].is_group_ext:
            self.track_index_group -= 2

        super(GroupTrack, self).__init__(song, self.group.track, self.track_index_group)

        self.midi.g_track = self.audio.g_track = self

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
    def midi(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 1]

    @property
    def audio(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 2]

    @property
    def arm(self):
        # type: () -> bool
        return self.midi.arm and self.audio.arm

    @property
    def any_armed(self):
        # type: () -> bool
        return self.midi.arm or self.audio.arm

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
        self.group.color = color
        self.midi.color = color
        self.audio.color = color

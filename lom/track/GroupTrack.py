from typing import TYPE_CHECKING, Any

from a_protocol_0.consts import RECORDING_TIME_ONLY_AUDIO, GROUP_MINITAUR_NAME, GROUP_PROPHET_NAME
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.GroupTrackActionMixin import GroupTrackActionMixin
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0 import Protocol0Component
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song


class GroupTrack(GroupTrackActionMixin, AbstractTrack):
    def __init__(self, base_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        from a_protocol_0 import Protocol0Component
        self.parent = Protocol0Component.SELF  # accessing parent here so because we need it before AbstractObject instantiation
        self.track_index_group = base_track.index

        if not base_track.is_groupable:
            raise Exception(
                "tried to instantiate non group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                            self.track_index_group))
        # allow actions to be executed on nested group tracks
        if base_track.is_nested_group_ex_track:
            self.track_index_group -= 1 if base_track.is_midi else 2

        super(GroupTrack, self).__init__(self.song.tracks[self.track_index_group], self.track_index_group, *a, **k)
        self.group.g_track = self.midi.g_track = self.audio.g_track = self
        self.recording_times.append(RECORDING_TIME_ONLY_AUDIO)

    @property
    def track(self):
        # type: () -> int
        return self.group.track

    @property
    def index(self):
        # type: () -> int
        return self.group.index

    @property
    def next_empty_clip_slot(self):
        # type: () -> ClipSlot
        return self.audio.next_empty_clip_slot

    @property
    def is_simple_group(self):
        # type: () -> bool
        return False

    @property
    def is_foldable(self):
        # type: () -> bool
        return True

    @property
    def selectable_track(self):
        # type: () -> SimpleTrack
        return self.midi

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
        if self.name == GROUP_PROPHET_NAME:
            return Colors.PROPHET
        elif self.name == GROUP_MINITAUR_NAME:
            return Colors.MINITAUR
        return Colors.DISABLED

    @color.setter
    def color(self, color):
        # type: (int) -> None
        self.group.color = color
        self.midi.color = color
        self.audio.color = color

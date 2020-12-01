from typing import TYPE_CHECKING, Any

from a_protocol_0.lom.ClipSlot import ClipSlot
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
        # accessing parent here so because we need it before AbstractObject instantiation
        self.parent = Protocol0Component.SELF  # type: Protocol0Component
        self.track_index_group = base_track.index

        if not base_track.is_groupable:
            raise Exception(
                "tried to instantiate non group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                            self.track_index_group))
        # allow actions to be executed on nested group tracks
        if base_track.is_nested_group_ex_track:
            self.track_index_group -= 1 if base_track.is_midi else 2

        super(GroupTrack, self).__init__(self.parent.song._song.tracks[self.track_index_group], self.track_index_group, *a, **k)
        self.group.g_track = self.midi.g_track = self.audio.g_track = self

        if not self.arm:
            self.is_folded = True

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
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.midi.is_recording or self.audio.is_recording

    @property
    def base_color(self):
        # type: () -> int
        return self.instrument.COLOR

    @property
    def color(self):
        # type: () -> int
        return self.group.color

    @color.setter
    def color(self, color):
        # type: (int) -> None
        self.group.color = color
        self.midi.color = color
        self.audio.color = color

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> ClipSlot
        for i in range(len(self.song.scenes)):
            if not self.midi.clip_slots[i].has_clip and not self.audio.clip_slots[i].has_clip:
                return i
        self.song.create_scene()
        return len(self.song.scenes) - 1

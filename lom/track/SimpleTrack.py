from functools import partial
from typing import Any, Optional, TYPE_CHECKING

from a_protocol_0.consts import GROUP_EXT_NAMES
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.GroupTrack import GroupTrack


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    def __init__(self, *a, **k):
        super(SimpleTrack, self).__init__(*a, **k)
        self.clip_slots = self.build_clip_slots()
        self._base_color = self.color
        self.group_track = None
        self.attach_to_group()

    def __hash__(self):
        return self.index

    def init_listeners(self):
        if self._track.playing_slot_index_has_listener(self.playing_slot_index_listener):
            self._track.remove_playing_slot_index_listener(self.playing_slot_index_listener)
        self._track.add_playing_slot_index_listener(self.playing_slot_index_listener)

    def playing_slot_index_listener(self, execute_later=True):
        # type: (bool) -> None
        if execute_later:
            return self.parent.wait(1, partial(self.playing_slot_index_listener, execute_later=False))
        self.build_clip_slots()
        if self.playing_slot_index >= 0:
            self.name = TrackName(self).get_track_name_for_clip_index(self.playing_slot_index)
            clip = self.clip_slots[self.playing_slot_index].clip
            if clip:
                clip.color = self.base_color

    def build_clip_slots(self):
        # type: () -> list[ClipSlot]
        return [ClipSlot(clip_slot=clip_slot, index=index, track=self) for (index, clip_slot) in enumerate(list(self._track.clip_slots))]

    def refresh_name(self):
        # type: () -> None
        self.name = TrackName(self).get_track_name_for_clip_index(self.playing_slot_index)

    def attach_to_group(self):
        self.parent.log(", ".join(self.output_routings))
        for group_track in list(reversed(self.song.group_tracks)):
            if self.group_output_routing == group_track.name:
                self.group_track = group_track
                self.group_track.children.append(self)
                break
        if self.is_nested_track and not self.group_track:  # handles ableton auto track renaming
            self.group_track = self.song.group_tracks[-1]
            self.group_track.children.append(self)

    def set_clip_color(self):
        # type: () -> None
        if self.playing_slot_index >= 0:
            self.name = TrackName(self).get_track_name_for_clip_index(self.playing_slot_index)

    @property
    def is_groupable(self):
        # type: () -> bool
        return self.name in GROUP_EXT_NAMES or self.is_nested_group_ex_track

    @property
    def is_nested_group_ex_track(self):
        # type: () -> bool
        return self.group_output_routing in GROUP_EXT_NAMES

    @property
    def is_nested_track(self):
        # type: () -> bool
        return self.current_output_routing == "Group"

    @property
    def is_audio(self):
        # type: () -> bool
        return self._track.has_audio_input

    @property
    def is_midi(self):
        # type: () -> bool
        return self._track.has_midi_input

    @property
    def is_simpler(self):
        # type: () -> bool
        return len(self.devices) and self.devices[0].class_name == "OriginalSimpler"

    @property
    def is_playing(self):
        # type: () -> bool
        return bool(self.playable_clip) and self.playable_clip.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return any([clip_slot for clip_slot in self.clip_slots if clip_slot.has_clip and clip_slot.clip.is_recording])

    @property
    def is_triggered(self):
        # type: () -> bool
        return any([clip_slot.is_triggered for clip_slot in self.clip_slots])

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track.is_visible

    @property
    def is_top_visible(self):
        # type: () -> bool
        return self.is_visible and not self.is_nested_group_ex_track

    @property
    def devices(self):
        # type: () -> list[Any]
        return self._track.devices

    @property
    def playing_slot_index(self):
        # type: () -> int
        if self._track.playing_slot_index >= 0:
            return self._track.playing_slot_index
        elif TrackName(self).clip_slot_index and TrackName(self).clip_slot_index in self.clip_slots:
            return TrackName(self).clip_slot_index
        return self._track.playing_slot_index

    @property
    def playable_clip(self):
        # type: () -> Clip
        playing_clip_slot = self.clip_slots[self.playing_slot_index] if self.playing_slot_index >= 0 else None
        if playing_clip_slot:
            return playing_clip_slot.clip
        elif TrackName(self).clip_slot_index >= 0 and self.clip_slots[TrackName(self).clip_slot_index].has_clip:
            return self.clip_slots[TrackName(self).clip_slot_index].clip
        return Clip.empty_clip()

    @property
    def clips(self):
        # type: () -> list[Clip]
        return [clip_slot.clip for clip_slot in self.clip_slots]

    @property
    def arm(self):
        # type: () -> bool
        return self.can_be_armed and self._track.arm

    @arm.setter
    def arm(self, arm):
        # type: (bool) -> None
        self._track.arm = arm if self.can_be_armed else None

    @property
    def mute(self):
        # type: () -> bool
        return self._track.mute

    @mute.setter
    def mute(self, mute):
        # type: (bool) -> None
        self._track.mute = mute

    @property
    def solo(self):
        # type: () -> bool
        return self._track.solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        self._track.solo = solo

    @property
    def base_color(self):
        # type: () -> int
        return self.g_track.base_color if self.is_groupable else self._base_color

    @property
    def color(self):
        # type: () -> int
        return self._track.color_index

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self._track.color_index = color_index

    @property
    def is_selected(self):
        # type: () -> bool
        return self.song.selected_track == self

    @is_selected.setter
    def is_selected(self, is_selected):
        # type: (bool) -> None
        self.song.selected_track = self if is_selected else None

    @property
    def current_output_routing(self):
        # type: () -> str
        return self._track.current_output_routing

    @property
    def output_routings(self):
        # type: () -> list
        return list(self._track.output_routings)

    @property
    def group_output_routing(self):
        # type: () -> Optional[str]
        if len(self.output_routings) < 3:
            return "Master"
        group_output_routing = str(self.output_routings[2])
        return group_output_routing if group_output_routing in self.song.group_tracks_names else "Master"

    @property
    def has_monitor_in(self):
        # type: () -> bool
        return self._track.current_monitoring_state == 0

    @has_monitor_in.setter
    def has_monitor_in(self, has_monitor_in):
        # type: (bool) -> None
        self._track.current_monitoring_state = int(not has_monitor_in)

    @property
    def empty_clip_slots(self):
        # type: () -> list[ClipSlot]
        return [clip_slot for clip_slot in self.clip_slots if not clip_slot.has_clip]

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> int
        if len(self.empty_clip_slots):
            return self.empty_clip_slots[0].index
        else:
            self.song.create_scene()
            return len(self.song.scenes) - 1

    @property
    def base_name(self):
        # type: () -> str
        base_name = TrackName(self).name
        return base_name[0].upper() + base_name[1:]

    @property
    def preset_index(self):
        # type: () -> int
        return TrackName(self).preset_index

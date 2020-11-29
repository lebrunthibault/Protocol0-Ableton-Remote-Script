from functools import partial
from typing import Any, Optional, TYPE_CHECKING

from a_protocol_0.consts import GROUP_EXT_NAMES
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.lom.track.SimpleTrackListenerMixin import SimpleTrackListenerMixin
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.GroupTrack import GroupTrack


class SimpleTrack(SimpleTrackActionMixin, SimpleTrackListenerMixin, AbstractTrack):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleTrack, self).__init__(*a, **k)
        self.clip_slots = self.build_clip_slots()

    def __hash__(self):
        return self.index

    def init_listeners(self):
        # type: ("SimpleTrack") -> None
        if self.track.playing_slot_index_has_listener(self.playing_slot_index_listener):
            self.track.remove_playing_slot_index_listener(self.playing_slot_index_listener)
        self.track.add_playing_slot_index_listener(self.playing_slot_index_listener)

    def playing_slot_index_listener(self, execute_later=True):
        # type: ("SimpleTrack", bool) -> None
        if execute_later:
            return self.parent.wait(1, partial(self.playing_slot_index_listener, execute_later=False))
        self.build_clip_slots()
        self.refresh_name()

    def build_clip_slots(self):
        # type: () -> list[ClipSlot]
        return [ClipSlot(clip_slot=clip_slot, index=index, track=self) for (index, clip_slot) in enumerate(list(self.track.clip_slots))]

    def refresh_name(self):
        # type: () -> None
        if self.playing_slot_index >= 0:
            self.name = TrackName(self).get_track_name_for_clip_index(self.playing_slot_index)

    @property
    def index(self):
        return self._index

    @property
    def track(self):
        return self._track

    @property
    def is_foldable(self):
        # type: () -> bool
        return self.track.is_foldable

    @property
    def is_simple_group(self):
        # type: () -> bool
        return self.is_foldable

    @property
    def is_groupable(self):
        # type: () -> bool
        return self.name in GROUP_EXT_NAMES or self.is_nested_group_ex_track

    @property
    def is_nested_group_ex_track(self):
        # type: () -> bool
        return any([routing in GROUP_EXT_NAMES for routing in self.output_routings])

    @property
    def abstract_track(self):
        # type: () -> AbstractTrack
        return self.g_track if self.is_groupable else self

    @property
    def is_audio(self):
        # type: () -> bool
        return self.track.has_audio_input

    @property
    def is_midi(self):
        # type: () -> bool
        return self.track.has_midi_input

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
    def selectable_track(self):
        # type: () -> SimpleTrack
        return self

    @property
    def is_visible(self):
        # type: () -> bool
        return self.track.is_visible

    @property
    def is_top_visible(self):
        # type: () -> bool
        return self.is_visible and not self.is_nested_group_ex_track

    @property
    def devices(self):
        # type: () -> list[Any]
        return self.track.devices

    @property
    def playing_slot_index(self):
        # type: () -> int
        if self.track.playing_slot_index >= 0:
            return self.track.playing_slot_index
        elif TrackName(self).clip_slot_index and TrackName(self).clip_slot_index in self.clip_slots:
            return TrackName(self).clip_slot_index
        return self.track.playing_slot_index

    @property
    def playing_clip_slot(self):
        # type: () -> Optional[ClipSlot]
        return self.clip_slots[self.playing_slot_index] if self.playing_slot_index >= 0 else None

    @property
    def playable_clip(self):
        # type: () -> Clip
        if self.playing_clip_slot:
            return self.playing_clip_slot.clip
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
        return self.can_be_armed and self.track.arm

    @arm.setter
    def arm(self, arm):
        # type: (bool) -> None
        if self.can_be_armed:
            self.track.arm = arm

    @property
    def mute(self):
        # type: () -> bool
        return self.track.mute

    @mute.setter
    def mute(self, mute):
        # type: (bool) -> None
        self.track.mute = mute

    @property
    def color(self):
        # type: () -> int
        return self.track.color_index

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.track.color_index = color_index

    @property
    def is_selected(self):
        # type: () -> bool
        return self.song.selected_track == self

    @is_selected.setter
    def is_selected(self, is_selected):
        # type: (bool) -> None
        if is_selected:
            self.song.selected_track = self

    @property
    def can_be_armed(self):
        # type: () -> bool
        return self.track.can_be_armed

    @property
    def output_routings(self):
        # type: () -> list
        return list(self.track.output_routings)

    @property
    def has_monitor_in(self):
        # type: () -> bool
        return self.track.current_monitoring_state == 0

    @has_monitor_in.setter
    def has_monitor_in(self, has_monitor_in):
        # type: (bool) -> None
        self.track.current_monitoring_state = int(not has_monitor_in)

    @property
    def next_empty_clip_slot(self):
        # type: () -> ClipSlot
        """ counting in live index """
        empty_clip_slot = next(
            iter([clip_slot for clip_slot in self.clip_slots if not clip_slot.has_clip]), None)
        if empty_clip_slot is None:
            self.song.create_scene()
            return self.next_empty_clip_slot

        return empty_clip_slot

    @property
    def base_name(self):
        # type: () -> str
        base_name = TrackName(self).name
        return base_name[0].upper() + base_name[1:]

    @property
    def preset_index(self):
        # type: () -> int
        return TrackName(self).preset_index

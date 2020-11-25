from functools import partial
from typing import Any, Optional, TYPE_CHECKING

from a_protocol_0.actions.mixins.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument
from a_protocol_0.instruments.AbstractInstrumentFactory import AbstractInstrumentFactory
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.GroupTrack import GroupTrack
from a_protocol_0.utils.log import log


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    SAMPLE_PATH = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported"

    def __init__(self, song, track, index):
        # type: (Any, Any, int) -> None
        super(SimpleTrack, self).__init__(song, track, index)
        self.g_track = None  # type: Optional[GroupTrack]

        self.clip_slots = self.build_clip_slots()

        if self.track.playing_slot_index_has_listener(self.playing_slot_index_listener):
            self.track.remove_playing_slot_index_listener(self.playing_slot_index_listener)
        self.track.add_playing_slot_index_listener(self.playing_slot_index_listener)
        self._last_playing_clip = None

    def __hash__(self):
        return self.index

    # @property
    # def last_clip_playing(self):
    #     # type: () -> Clip
    #     return self._last_playing_clip
    #
    # def set_last_clip_playing(self):
    #     # type: () -> None
    #     self._last_playing_clip = self.playable_clip

    def playing_slot_index_listener(self, execute_later=True):
        if execute_later:
            return self.parent.wait(1, partial(self.playing_slot_index_listener, execute_later=False))

        self.build_clip_slots()
        self.refresh_name()

    def build_clip_slots(self):
        # type: () -> list[ClipSlot]
        return [ClipSlot(clip_slot, index, self) for (index, clip_slot) in enumerate(list(self.track.clip_slots))]

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
    def instrument(self):
        # type: () -> AbstractInstrument
        return AbstractInstrumentFactory.create_from_simple_track(self)

    @property
    def is_foldable(self):
        # type: () -> bool
        return self.track.is_foldable

    @property
    def is_folded(self):
        # type: () -> bool
        return self.track.fold_state if self.is_foldable else False

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if self.is_foldable:
            self.track.fold_state = int(is_folded)

    @property
    def is_simple_group(self):
        # type: () -> bool
        return self.is_foldable

    @property
    def is_groupable(self):
        # type: () -> bool
        return self.is_group_ext or \
               (self.index >= 1 and self.song.tracks[self.index - 1].is_group_ext) or \
               (self.index >= 2 and self.song.tracks[self.index - 2].is_group_ext)

    @property
    def is_group_ext(self):
        # type: () -> bool
        return self.name in TrackName.GROUP_EXT_NAMES

    @property
    def is_nested_group_ex_track(self):
        # type: () -> bool
        return (self.index >= 1 and self.song.tracks[self.index - 1].is_group_ext) or \
               (self.index >= 2 and self.song.tracks[self.index - 2].is_group_ext)

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

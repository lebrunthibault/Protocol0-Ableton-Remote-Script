from functools import partial
from typing import List

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.consts import GROUP_EXT_NAMES
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.lom.track.TrackName import TrackName


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    def __init__(self, *a, **k):
        super(SimpleTrack, self).__init__(*a, **k)
        self.clip_slots = []  # type: List[ClipSlot]
        self.clips = []  # type: List[Clip]
        self.build_clip_slots()
        # defer till Live is stopped because it boots playing
        self.parent._wait(10, lambda: setattr(self.playing_slot_index_listener, "subject", self._track))

    def __hash__(self):
        return self.index

    @subject_slot("playing_slot_index")
    def playing_slot_index_listener(self, execute_later=True):
        # type: (bool) -> None
        if execute_later:
            return self.parent.defer(partial(self.playing_slot_index_listener, execute_later=False))
        if self.playing_slot_index >= 0:
            clip = self.clip_slots[self.playing_slot_index].clip
            if clip:
                clip.color = self.base_color
                if clip.is_playing:
                    self.name = TrackName(self).get_track_name_for_clip_index(self.playing_slot_index)

    @property
    def is_external_synth_sub_track(self):
        return self.group_track and self.group_track.name in GROUP_EXT_NAMES

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
    def playing_slot_index(self):
        # type: () -> int
        """ returns Live playing_slot_index or """
        if self._track.playing_slot_index >= 0:
            return self._track.playing_slot_index
        else:
            return TrackName(self).clip_slot_index

    @property
    def playable_clip(self):
        # type: () -> Clip
        clip = self.clip_slots[self.playing_slot_index].clip if self.playing_slot_index >= 0 else None
        if clip:
            return clip
        elif len(self.clips):
            return self.clips[0]
        else:
            return Clip.empty_clip()

    @property
    def arm(self):
        # type: () -> bool
        return self.can_be_armed and self._track.arm

    @arm.setter
    def arm(self, arm):
        # type: (bool) -> None
        if self.can_be_armed:
            self._track.arm = arm

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
    def is_selected(self):
        # type: () -> bool
        return self.song.selected_track == self

    @is_selected.setter
    def is_selected(self, is_selected):
        # type: (bool) -> None
        if is_selected:
            self.song.select_track(self)

    @property
    def has_monitor_in(self):
        # type: () -> bool
        return self._track.current_monitoring_state == 0

    @has_monitor_in.setter
    def has_monitor_in(self, has_monitor_in):
        # type: (bool) -> None
        self._track.current_monitoring_state = int(not has_monitor_in)

    @property
    def _empty_clip_slots(self):
        # type: () -> List[ClipSlot]
        return [clip_slot for clip_slot in self.clip_slots if not clip_slot.has_clip]

    @property
    def _next_empty_clip_slot_index(self):
        # type: () -> int
        if len(self._empty_clip_slots):
            return self._empty_clip_slots[0].index
        else:
            self.song.create_scene()
            return len(self.song.scenes) - 1

from typing import List

from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if
from a_protocol_0.consts import EXTERNAL_SYNTH_NAMES
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    def __init__(self, *a, **k):
        super(SimpleTrack, self).__init__(*a, **k)
        self.clip_slots = []  # type: List[ClipSlot]
        self._map_clip_slots.subject = self._track
        self._map_clip_slots()
        # defer till Live is stopped because it boots playing
        self.parent._wait(10, lambda: setattr(self.playing_slot_index_listener, "subject", self._track))

    def __hash__(self):
        return self.index

    @subject_slot("notes")
    def observe_clip_notes(self):
        # type: (SimpleTrack) -> None
        pass

    @subject_slot("clip_slots")
    def _map_clip_slots(self):
        # type: (SimpleTrack) -> None
        self.clip_slots = [ClipSlot(clip_slot=clip_slot, index=index, track=self) for (index, clip_slot) in
                           enumerate(list(self._track.clip_slots))]

    @subject_slot("playing_slot_index")
    @defer
    def playing_slot_index_listener(self):
        # type: () -> None
        if self.playing_slot_index < 0:
            return
        clip = self.clip_slots[self.playing_slot_index].clip
        if not clip:
            return
        clip.color = self.base_color
        if clip.is_playing:
            TrackName(self).set(clip_slot_index=self.playing_slot_index)
            [setattr(clip, "is_selected", False) for clip in self.clips]

    @property
    def is_external_synth_sub_track(self):
        return self.group_track and self.group_track.name in EXTERNAL_SYNTH_NAMES

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
        selected_clip = find_if(lambda clip: clip.is_selected, self.clips)
        if selected_clip:
            return selected_clip
        clip = self.clip_slots[self.playing_slot_index].clip
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

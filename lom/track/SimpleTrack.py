from typing import List, Optional

from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.Util import find_if
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    __subject_events__ = ('base_name',)

    def __init__(self, *a, **k):
        super(SimpleTrack, self).__init__(*a, **k)
        self.clip_slots = []  # type: List[ClipSlot]
        self._clip_slots_listener.subject = self._track
        self._clip_slots_listener()
        self._playing_slot_index_listener.subject = self._track
        self.base_name = self.name
        self._name_listener.subject = self._track
        self.instrument = self.parent.deviceManager.create_instrument_from_simple_track(track=self)  # AbstractInstrument

    def __hash__(self):
        return self.index

    @subject_slot("name")
    def _name_listener(self):
        if self.name != self.base_name:
            self.base_name = self.name
            # noinspection PyUnresolvedReferences
            self.notify_base_name()

    @subject_slot_group("notes")
    def _clip_notes_listener(self, clip):
        # type: (SimpleTrack) -> None
        pass

    @subject_slot("clip_slots")
    def _clip_slots_listener(self):
        # type: (SimpleTrack) -> None
        self.clip_slots = [ClipSlot(clip_slot=clip_slot, index=index, track=self) for (index, clip_slot) in
                           enumerate(list(self._track.clip_slots))]

    @subject_slot("playing_slot_index")
    @defer
    def _playing_slot_index_listener(self):
        # type: () -> None
        if self.playing_slot_index < 0:
            return
        clip = self.clip_slots[self.playing_slot_index].clip
        if not clip:
            return
        clip.color = self.base_color
        if clip.is_playing:
            return
            TrackName(self).clip_slot_index = self.playing_slot_index
            [setattr(clip, "is_selected", False) for clip in self.clips]

    @property
    def is_external_synth_sub_track(self):
        return self.group_track and self.group_track.is_external_synth_track

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
            return self.clip_slot_index

    @property
    def playable_clip(self):
        # type: () -> Optional[Clip]
        selected_clip = find_if(lambda clip: clip.is_selected, self.clips)
        if selected_clip:
            return selected_clip
        if self.clip_slots[self.playing_slot_index].has_clip:
            return self.clip_slots[self.playing_slot_index].clip
        elif len(self.clips):
            return self.clips[0]
        else:
            return None

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
    def volume(self):
        # type: () -> float
        return self._track.mixer_device.volume.value

    @volume.setter
    @defer
    def volume(self, volume):
        # type: (float) -> None
        self._track.mixer_device.volume.value = volume

    @property
    def _next_empty_clip_slot_index(self):
        # type: () -> int
        index = None
        if len(self.clips):
            index = next(iter([cs.index for cs in self._empty_clip_slots if cs.index > self.clips[-1].index]), None)
        elif len(self._empty_clip_slots):
            index = self._empty_clip_slots[0].index
        if index is None:
            self.song.create_scene()
            index = len(self.song.scenes) - 1

        return index

import Live
from typing import List, Optional

from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.lom.track.simple_track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.utils.decorators import defer


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    __subject_events__ = ('base_name',)

    def __init__(self, track, index, *a, **k):
        # type: (Live.Track.Track, int) -> None
        self._track = track
        self.index = index
        super(SimpleTrack, self).__init__(track=self, *a, **k)
        if self.group_track:
            self.group_track.sub_tracks.append(self)
        self.clip_slots = []  # type: List[ClipSlot]
        self._clip_slots_listener.subject = self._track
        self._clip_slots_listener()
        self._playing_slot_index_listener.subject = self._track
        self.devices = []  # type: List[Device]
        self._devices_listener.subject = self._track
        self._devices_listener()
        self.base_name = self.name
        self._name_listener.subject = self._track
        self.instrument = self.parent.deviceManager.create_instrument_from_simple_track(track=self)
        if self.is_midi:  # could later create a SimpleMidiTrack class if necessary
            self.push2_selected_matrix_mode = 'note'
            self.push2_selected_instrument_mode = 'split_melodic_sequencer'

    def __hash__(self):
        return self.index

    @subject_slot("name")
    def _name_listener(self):
        if self.name != self.base_name:
            self.base_name = self.name
            # noinspection PyUnresolvedReferences
            self.notify_base_name()

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
        if clip.is_playing:
            TrackName(self).clip_slot_index = self.playing_slot_index
            [setattr(clip, "is_selected", False) for clip in self.clips]

    @subject_slot("devices")
    def _devices_listener(self):
        # type: (SimpleTrack) -> None
        self.devices = [Device(device, self.base_track) for device in self._track.devices]

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
    def _empty_clip_slots(self):
        # type: () -> List[ClipSlot]
        return [clip_slot for clip_slot in self.clip_slots if not clip_slot.has_clip]

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

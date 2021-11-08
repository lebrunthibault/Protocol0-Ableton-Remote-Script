from itertools import chain

from typing import List, Optional, Any, Dict

import Live
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.lom.clip.Clip import Clip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.device.Device import Device
from protocol0.lom.device.DeviceParameter import DeviceParameter
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.simple_track.SimpleTrackActionMixin import SimpleTrackActionMixin
from protocol0.utils.decorators import p0_subject_slot
from protocol0.utils.utils import find_if


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    CLIP_CLASS = Clip

    def __init__(self, track, *a, **k):
        # type: (Live.Track.Track, Any, Any) -> None
        self._track = track  # type: Live.Track.Track
        super(SimpleTrack, self).__init__(track=self, *a, **k)

        # is_active is used to differentiate set tracks for return / master
        # we act only on active tracks

        # Note : SimpleTracks represent the first layer of abstraction and know nothing about
        # AbstractGroupTracks except with self.abstract_group_track which links both layers
        self.sub_tracks = []  # type: List[SimpleTrack]

        self.linked_track = None  # type: Optional[SimpleTrack]
        self.devices = []  # type: List[Device]
        self.all_devices = []  # type: List[Device]
        self._instrument = None  # type: Optional[AbstractInstrument]
        self._devices_listener.subject = self._track
        self._devices_listener()
        self.clip_slots = []  # type: List[ClipSlot]

        if self.is_active:
            self._fired_slot_index_listener.subject = self._track

            self.map_clip_slots()

    @property
    def is_active(self):
        # type: () -> bool
        return self._track not in list(self.song._song.return_tracks) + [self.song._song.master_track]

    def link_group_track(self):
        # type: () -> None
        # register to the group track
        if self._track.group_track:
            self.group_track = self.song.live_track_to_simple_track[
                self._track.group_track
            ]  # type: Optional[AbstractTrack]
            self.group_track.sub_tracks.append(self)

    def map_clip_slots(self):
        # type: () -> Any
        """ create new ClipSlot objects and keep existing ones """
        live_clip_slot_to_clip_slot = {}  # type: Dict[Live.ClipSlot.ClipSlot, ClipSlot]
        for clip_slot in self.clip_slots:
            live_clip_slot_to_clip_slot[clip_slot._clip_slot] = clip_slot
        new_clip_slots = []  # type: List[ClipSlot]
        for (i, clip_slot) in enumerate(list(self._track.clip_slots)):
            if clip_slot in live_clip_slot_to_clip_slot:
                new_clip_slots.append(live_clip_slot_to_clip_slot[clip_slot])
            else:
                new_clip_slots.append(ClipSlot.make(clip_slot=clip_slot, track=self))
        self.clip_slots = new_clip_slots
        self._clip_slots_has_clip_listener.replace_subjects(self.clip_slots)

    @p0_subject_slot("fired_slot_index")
    def _fired_slot_index_listener(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        self.parent.defer(self.notify_fired_slot_index)

    @subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        for device in self.devices:
            device.disconnect()

        self.devices = [Device.make(device, self) for device in self._track.devices]
        self.all_devices = self.find_all_devices(self.base_track)

        # noinspection PyUnresolvedReferences
        self.notify_devices()

        # Refreshing is only really useful from simpler devices that change when a new sample is loaded
        if self.is_active and not self.is_foldable:
            self.instrument = self.parent.deviceManager.make_instrument_from_simple_track(track=self)
            # notify instrument change on both the device track and the abstract_group_track
            if self.instrument:
                # noinspection PyUnresolvedReferences
                self.abstract_track.notify_instrument()

    @subject_slot_group("has_clip")
    def _clip_slots_has_clip_listener(self, _):
        # type: (ClipSlot) -> None
        # noinspection PyUnresolvedReferences
        self.notify_has_clip()
        if self.abstract_group_track:
            # noinspection PyUnresolvedReferences
            self.abstract_group_track.notify_has_clip()
        pass

    @property
    def is_armed(self):
        # type: () -> bool
        return self.can_be_armed and self._track.arm

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        if self.can_be_armed:
            self._track.arm = is_armed

    @property
    def is_armable(self):
        # type: () -> bool
        """ Checks for disabled input routing """
        if not self.can_be_armed:
            return True
        self.is_armed = True
        if self.is_armed:
            self.is_armed = False
            return True
        else:
            return False

    @property
    def current_monitoring_state(self):
        # type: () -> CurrentMonitoringStateEnum
        return CurrentMonitoringStateEnum.get_from_value(self._track.current_monitoring_state)

    @current_monitoring_state.setter
    def current_monitoring_state(self, monitoring_state):
        # type: (CurrentMonitoringStateEnum) -> None
        self._track.current_monitoring_state = monitoring_state.value

    @property
    def playing_slot_index(self):
        # type: () -> int
        return self._track.playing_slot_index

    @property
    def fired_slot_index(self):
        # type: () -> int
        return self._track.fired_slot_index

    @property
    def active_tracks(self):
        # type: () -> List[AbstractTrack]
        raise [self]

    @property
    def device_parameters(self):
        # type: () -> List[DeviceParameter]
        return list(chain(*[device.parameters for device in self.all_devices]))

    @property
    def instrument(self):
        # type: () -> Optional[AbstractInstrument]
        return self._instrument
        # return getattr(self, "_instrument", None)

    @instrument.setter
    def instrument(self, instrument):
        # type: (AbstractInstrument) -> None
        self._instrument = instrument

    @property
    def is_audio(self):
        # type: () -> bool
        from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack

        return isinstance(self, SimpleAudioTrack) and self._track.has_audio_input

    @property
    def is_midi(self):
        # type: () -> bool
        from protocol0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack

        return isinstance(self, SimpleMidiTrack) and self._track.has_midi_input

    @property
    def is_playing(self):
        # type: () -> bool
        return any(clip_slot.is_playing for clip_slot in self.clip_slots)

    @property
    def is_triggered(self):
        # type: () -> bool
        return any(clip_slot.is_triggered for clip_slot in self.clip_slots)

    @property
    def is_recording(self):
        # type: () -> bool
        return any(clip for clip in self.clips if clip.is_recording)

    @property
    def device_insert_mode(self):
        # type: () -> Live.Track.DeviceInsertMode
        return self._track.view.device_insert_mode

    @device_insert_mode.setter
    def device_insert_mode(self, device_insert_mode):
        # type: (Live.Track.DeviceInsertMode) -> None
        self._track.view.device_insert_mode = device_insert_mode

    @property
    def playing_clip(self):
        # type: () -> Optional[Clip]
        """ Returns the currently playing clip is any """
        return self.clip_slots[self.playing_slot_index].clip if self.playing_slot_index >= 0 else None

    @property
    def playable_clip(self):
        # type: () -> Optional[Clip]
        return self.playing_clip or self.clip_slots[self.song.selected_scene.index].clip

    @property
    def selected_device(self):
        # type: (SimpleTrack) -> Optional[Device]
        if self._track.view.selected_device:
            device = find_if(
                lambda d: d._device == self._track.view.selected_device, self.base_track.all_devices
            )  # type: Optional[Device]
            assert device
            return device
        else:
            return None

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        for i in range(self.song.selected_scene.index, len(self.song.scenes)):
            if not self.clip_slots[i].clip:
                return i

        return None

    def disconnect(self):
        # type: () -> None
        super(SimpleTrack, self).disconnect()
        for device in self.devices:
            device.disconnect()
        for clip_slot in self.clip_slots:
            clip_slot.disconnect()
        if self.instrument:
            self.instrument.disconnect()

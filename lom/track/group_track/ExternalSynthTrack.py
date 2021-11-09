import itertools

from typing import Optional, Any, cast, List

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.DeviceParameterNameEnum import DeviceParameterNameEnum
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.lom.device.Device import Device
from protocol0.lom.device.DeviceSynchronizer import DeviceSynchronizer
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from protocol0.lom.track.group_track.ExternalSynthTrackName import ExternalSynthTrackName
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.lom.track.simple_track.TrackSynchronizer import TrackSynchronizer
from protocol0.utils.decorators import p0_subject_slot
from protocol0.utils.utils import find_if


class ExternalSynthTrack(ExternalSynthTrackActionMixin, AbstractGroupTrack):
    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track=base_group_track, *a, **k)
        self.midi_track = base_group_track.sub_tracks[0]
        self.audio_track = base_group_track.sub_tracks[1]
        assert isinstance(self.midi_track, SimpleMidiTrack) and isinstance(self.audio_track, SimpleAudioTrack), (
                "invalid external synth track %s" % self
        )

        self._external_device = None  # type: Optional[Device]
        self._devices_listener.subject = self.midi_track
        self._devices_listener()

        # audio and midi tracks are now handled by self
        self.audio_track.abstract_group_track = self
        self.midi_track.abstract_group_track = self

        self.track_name.disconnect()  # type: ignore[has-type]
        self.track_name = ExternalSynthTrackName(self)

        self._clip_slot_synchronizers = []  # type: List[ClipSlotSynchronizer]
        self._devices_synchronizers = []  # type: List[DeviceSynchronizer]

        with self.parent.component_guard():
            self._midi_audio_synchronizer = TrackSynchronizer(self.audio_track, self.midi_track, ["solo"])
            self._midi_solo_synchronizer = ObjectSynchronizer(self.base_track, self.midi_track, ["solo"])
            self._link_group_devices_to_audio_devices()

        # the instrument handling relies on the group track
        # noinspection PyUnresolvedReferences
        self.notify_instrument()

    def _link_clip_slots(self):
        # type: () -> None
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()

        with self.parent.component_guard():
            self._clip_slot_synchronizers = [
                ClipSlotSynchronizer(midi_clip_slot, audio_clip_slot)
                for midi_clip_slot, audio_clip_slot in itertools.izip(  # type: ignore[attr-defined]
                    self.midi_track.clip_slots, self.audio_track.clip_slots
                )
            ]

    def _link_group_devices_to_audio_devices(self):
        # type: () -> None
        """ allows recording session clip automation from the group track without using dummy clips """
        lfo_tool_group = self.base_track.get_device_from_enum(DeviceEnum.LFO_TOOL)
        lfo_tool_audio = self.audio_track.get_device_from_enum(DeviceEnum.LFO_TOOL)

        if lfo_tool_group and lfo_tool_audio:
            self._devices_synchronizers.append(
                DeviceSynchronizer(lfo_tool_group, lfo_tool_audio, [DeviceParameterNameEnum.LFO_TOOL_LFO_DEPTH]))

    def link_parent_and_child_objects(self):
        # type: () -> None
        super(ExternalSynthTrack, self).link_parent_and_child_objects()
        self._link_clip_slots()

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        self._external_device = find_if(lambda d: d.is_external_device, self.midi_track.devices)

    @property
    def instrument(self):
        # type: () -> AbstractInstrument
        return cast(AbstractInstrument, self.midi_track.instrument or self.audio_track.instrument)

    @property
    def can_be_armed(self):
        # type: () -> bool
        return True

    @property
    def is_armed(self):
        # type: () -> bool
        return self.audio_track.is_armed

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        for track in self.active_tracks:
            track.is_armed = is_armed

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi_track.is_playing or self.audio_track.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.midi_track.is_recording or self.audio_track.is_recording

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        for i in range(self.song.selected_scene.index, len(self.song.scenes)):
            if not self.midi_track.clip_slots[i].clip and not self.audio_track.clip_slots[i].clip:
                return i
        return None

    def set_output_routing_to(self, *a, **k):
        # type: (Any, Any) -> None
        self.audio_track.set_output_routing_to(*a, **k)

    @property
    def color(self):
        # type: () -> int
        return self.base_track.color

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.base_track.color = color_index
        self.midi_track.color = color_index
        self.audio_track.color = color_index

    def disconnect(self):
        # type: () -> None
        super(ExternalSynthTrack, self).disconnect()
        self._midi_solo_synchronizer.disconnect()
        self._midi_audio_synchronizer.disconnect()
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()
        self._clip_slot_synchronizers = []
        for device_synchronizer in self._devices_synchronizers:
            device_synchronizer.disconnect()
        self._devices_synchronizers = []

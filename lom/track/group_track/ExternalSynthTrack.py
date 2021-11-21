import itertools

from typing import Optional, Any, cast, List

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.lom.device.Device import Device
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from protocol0.lom.track.group_track.ExternalSynthTrackName import ExternalSynthTrackName
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot
from protocol0.utils.utils import find_if


class ExternalSynthTrack(ExternalSynthTrackActionMixin, AbstractGroupTrack):
    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track=base_group_track, *a, **k)
        self.midi_track = base_group_track.sub_tracks[0]
        self.audio_track = base_group_track.sub_tracks[1]
        self.dummy_tracks = []  # type: List[SimpleDummyTrack]
        assert isinstance(self.midi_track, SimpleMidiTrack) and isinstance(self.audio_track, SimpleAudioTrack), (
                "invalid external synth track %s" % self
        )

        # sub tracks are now handled by self
        self.audio_track.abstract_group_track = self
        self.midi_track.abstract_group_track = self

        self.track_name.disconnect()  # type: ignore[has-type]
        self.track_name = ExternalSynthTrackName(self)

        self._clip_slot_synchronizers = []  # type: List[ClipSlotSynchronizer]

        with self.parent.component_guard():
            self._midi_audio_synchronizer = ObjectSynchronizer(self.audio_track, self.midi_track, ["solo"])
            self._midi_solo_synchronizer = ObjectSynchronizer(self.base_track, self.midi_track, ["solo"])

        self._external_device = None  # type: Optional[Device]
        self._devices_listener.subject = self.midi_track
        self._devices_listener()

        self.protected_mode_active = True

        # the instrument handling relies on the group track
        # noinspection PyUnresolvedReferences
        self.notify_instrument()

    def _added_track_init(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(ExternalSynthTrack, self)._added_track_init)
        seq.add(self.abstract_track.arm)

        return seq.done()

    def _map_dummy_tracks(self):
        # type: () -> None
        dummy_tracks = self.base_track.sub_tracks[2:]
        self.dummy_tracks[:] = [self.parent.songManager.generate_simple_track(track=track._track, cls=SimpleDummyTrack) for track in dummy_tracks]

        for dummy_track in self.dummy_tracks:
            self.parent.log_dev("dummy_track: %s" % dummy_track)
            dummy_track.abstract_group_track = self

        self._link_dummy_tracks_routings()

    def _link_dummy_tracks_routings(self):
        # type: () -> None
        if len(self.dummy_tracks) == 0:
            return

        dummy_track = self.dummy_tracks[0]
        self.midi_track.output_routing_type = dummy_track
        self.audio_track.output_routing_type = dummy_track
        for next_dummy_track in self.dummy_tracks[1:]:
            dummy_track.output_routing_type = next_dummy_track
            dummy_track = next_dummy_track

    def link_clip_slots(self):
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

    def link_parent_and_child_tracks(self):
        # type: () -> None
        self._map_dummy_tracks()
        super(ExternalSynthTrack, self).link_parent_and_child_tracks()

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

import itertools

from typing import Optional, Any, cast, List, Iterator

from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.lom.clip.Clip import Clip
from protocol0.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.lom.device.Device import Device
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
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
        assert isinstance(self.midi_track, SimpleMidiTrack) and isinstance(self.audio_track, SimpleAudioTrack), (
                "invalid external synth track %s" % self
        )

        # sub tracks are now handled by self
        self.base_track.abstract_group_track = self
        self.audio_track.abstract_group_track = self
        self.midi_track.abstract_group_track = self

        self._clip_slot_synchronizers = []  # type: List[ClipSlotSynchronizer]

        with self.parent.component_guard():
            self._midi_audio_synchronizer = ObjectSynchronizer(self.audio_track, self.midi_track, ["solo"])
            self._midi_solo_synchronizer = ObjectSynchronizer(self.base_track, self.midi_track, ["solo"])

        self._external_device = None  # type: Optional[Device]
        self._devices_listener.subject = self.midi_track
        self._devices_listener()

        self.protected_mode_active = True  # type: bool

        # the instrument handling relies on the group track
        # noinspection PyUnresolvedReferences
        self.notify_instrument()

    def post_init(self):
        # type: () -> None
        super(ExternalSynthTrack, self).post_init()
        self.link_clip_slots()

    def _added_track_init(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(ExternalSynthTrack, self)._added_track_init)
        seq.add(self.abstract_track.arm)

        return seq.done()

    def _get_dummy_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        for track in self.base_track.sub_tracks[2:]:
            yield track

    def link_clip_slots(self):
        # type: () -> None
        if len(self._clip_slot_synchronizers) == len(self.midi_track.clip_slots):
            return

        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()

        with self.parent.component_guard():
            self._clip_slot_synchronizers = [
                ClipSlotSynchronizer(midi_clip_slot, audio_clip_slot)
                for midi_clip_slot, audio_clip_slot in itertools.izip(  # type: ignore[attr-defined]
                    self.midi_track.clip_slots, self.audio_track.clip_slots
                )
            ]

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        self._external_device = find_if(lambda d: d.is_external_device, self.midi_track.devices)

    @property
    def instrument(self):
        # type: () -> AbstractExternalSynthTrackInstrument
        return cast(AbstractExternalSynthTrackInstrument, self.midi_track.instrument or self.audio_track.instrument)

    @property
    def clips(self):
        # type: () -> List[Clip]
        clip_slots = self.midi_track.clip_slots + self.audio_track.clip_slots
        return [clip_slot.clip for clip_slot in clip_slots if clip_slot.has_clip and clip_slot.clip]

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
    def solo(self):
        # type: () -> bool
        return self.base_track.solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        self.base_track.solo = solo
        self.midi_track.solo = solo
        self.audio_track.solo = solo

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

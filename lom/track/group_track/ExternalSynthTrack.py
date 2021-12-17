import itertools

from typing import Optional, Any, cast, List, Iterator

from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.lom.clip.Clip import Clip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from protocol0.lom.device.Device import Device
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
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
        self.midi_track = cast(SimpleMidiTrack, base_group_track.sub_tracks[0])
        self.audio_track = cast(SimpleAudioTrack, base_group_track.sub_tracks[1])
        self.audio_tail_track = None  # type: Optional[SimpleAudioTailTrack]
        if len(base_group_track.sub_tracks) > 2 and len(base_group_track.sub_tracks[2].devices) == 0:
            # noinspection PyTypeChecker
            track = base_group_track.sub_tracks[2]
            self.audio_tail_track = self.parent.songManager.generate_simple_track(track=track._track,
                                                                                  cls=SimpleAudioTailTrack)

        self.parent.defer(self._rename_tracks_to_default)

        # sub tracks are now handled by self
        self.base_track.abstract_group_track = self
        for sub_track in base_group_track.sub_tracks:
            sub_track.abstract_group_track = self

        self._clip_slot_synchronizers = []  # type: List[ClipSlotSynchronizer]

        with self.parent.component_guard():
            self._midi_audio_synchronizer = ObjectSynchronizer(self.audio_track, self.midi_track, ["solo"])
            self._midi_audio_tail_synchronizer = None  # type: Optional[ObjectSynchronizer]
            if self.audio_tail_track:
                self._midi_audio_tail_synchronizer = ObjectSynchronizer(self.audio_tail_track, self.midi_track,
                                                                        ["solo"])
            self._midi_solo_synchronizer = ObjectSynchronizer(self.base_track, self.midi_track, ["solo"])

        self._external_device = None  # type: Optional[Device]
        self._devices_listener.subject = self.midi_track
        self._devices_listener()

        # the instrument handling relies on the group track
        # noinspection PyUnresolvedReferences
        self.notify_instrument()

        self.record_clip_tails = self.instrument.RECORD_CLIP_TAILS and self.audio_tail_track is not None
        self.parent.trackDataManager.restore_data(self)

    def on_grid_change(self):
        # type: () -> None
        super(ExternalSynthTrack, self).on_grid_change()
        self.link_clip_slots()

    def _added_track_init(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(super(ExternalSynthTrack, self)._added_track_init)
        seq.add(self.abstract_track.arm)

        if len(self.base_track.devices):
            seq.prompt("Clear %s effects ?" % len(self.base_track.devices))
            seq.add([device.delete for device in self.base_track.devices])

        return seq.done()

    def _get_dummy_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        main_tracks_length = 3 if self.audio_tail_track else 2
        for track in self.base_track.sub_tracks[main_tracks_length:]:
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
                for midi_clip_slot, audio_clip_slot in
                itertools.izip(  # type: ignore[attr-defined]
                    self.midi_track.clip_slots, self.audio_track.clip_slots
                )
            ]
            if self.audio_tail_track:
                self._clip_slot_synchronizers += [
                    ClipSlotSynchronizer(midi_clip_slot, audio_tail_clip_slot,
                                         no_muted=True)
                    for midi_clip_slot, audio_tail_clip_slot in
                    itertools.izip(  # type: ignore[attr-defined]
                        self.midi_track.clip_slots, self.audio_tail_track.clip_slots
                    )
                ]

    def _rename_tracks_to_default(self):
        # type: () -> None
        if self.midi_track.name != SimpleMidiTrack.DEFAULT_NAME:
            self.midi_track.name = SimpleMidiTrack.DEFAULT_NAME
        if self.audio_track.name != SimpleAudioTrack.DEFAULT_NAME:
            self.audio_track.name = SimpleAudioTrack.DEFAULT_NAME
        if self.audio_tail_track and self.audio_tail_track.name != SimpleAudioTailTrack.DEFAULT_NAME:
            self.audio_tail_track.name = SimpleAudioTailTrack.DEFAULT_NAME

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
        clip_slots = cast(List[ClipSlot],
                          self.midi_track.clip_slots) + self.audio_track.clip_slots
        if self.audio_tail_track:
            clip_slots += self.audio_tail_track.clip_slots

        return [clip_slot.clip for clip_slot in clip_slots if clip_slot.has_clip and clip_slot.clip]

    @property
    def can_be_armed(self):
        # type: () -> bool
        return True

    @property
    def is_armed(self):
        # type: () -> bool
        return all(sub_track.is_armed for sub_track in self.sub_tracks)

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        for track in self.sub_tracks:
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
        for sub_track in self.sub_tracks:
            sub_track.solo = solo

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
        for sub_track in self.sub_tracks:
            sub_track.color = color_index
            for clip in sub_track.clips:
                clip.color = color_index

    @property
    def computed_color(self):
        # type: () -> int
        return self.instrument.TRACK_COLOR.index

    def disconnect(self):
        # type: () -> None
        super(ExternalSynthTrack, self).disconnect()
        self._midi_solo_synchronizer.disconnect()
        self._midi_audio_synchronizer.disconnect()
        if self._midi_audio_tail_synchronizer:
            self._midi_audio_tail_synchronizer.disconnect()
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()
        self._clip_slot_synchronizers = []

import itertools

from typing import Optional, Any, Literal

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer
from a_protocol_0.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from a_protocol_0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from a_protocol_0.lom.track.simple_track.TrackSynchronizer import TrackSynchronizer


class ExternalSynthTrack(ExternalSynthTrackActionMixin, AbstractGroupTrack):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ExternalSynthTrack, self).__init__(*a, **k)
        self.midi_track = self.sub_tracks[0]
        self.audio_track = self.sub_tracks[1]
        assert isinstance(self.midi_track, SimpleMidiTrack) and isinstance(self.audio_track, SimpleAudioTrack), (
            "invalid external synth track %s" % self
        )

        with self.parent.component_guard():
            self._midi_audio_synchronizer = TrackSynchronizer(self.audio_track, self.midi_track)
            self._midi_track_synchronizer = ObjectSynchronizer(self.base_track, self.midi_track, "_track", ["solo"])

            self._clip_slot_synchronizers = [
                ClipSlotSynchronizer(midi_clip_slot, audio_clip_slot)
                for midi_clip_slot, audio_clip_slot in itertools.izip(  # type: ignore[attr-defined]
                    self.midi_track.clip_slots, self.audio_track.clip_slots
                )
            ]

        for sub_track in self.sub_tracks:
            sub_track.abstract_group_track = self
            sub_track.abstract_track = self

        self.audio_track.set_output_routing_to(self.base_track)

    @property
    def instrument(self):
        # type: () -> Optional[AbstractInstrument]
        return self.midi_track.instrument

    @property
    def can_be_armed(self):
        # type: () -> Literal[True]
        return True

    @property
    def is_armed(self):
        # type: () -> bool
        return self.midi_track.is_armed or self.audio_track.is_armed

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

    def disconnect(self):
        # type: () -> None
        super(ExternalSynthTrack, self).disconnect()
        self._midi_track_synchronizer.disconnect()
        self._midi_audio_synchronizer.disconnect()
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()

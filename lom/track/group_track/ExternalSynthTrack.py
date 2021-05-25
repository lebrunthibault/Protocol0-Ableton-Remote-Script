import itertools

from typing import Optional, Any, Literal, cast

from a_protocol_0.devices.AbstractInstrument import AbstractInstrument
from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer
from a_protocol_0.lom.clip_slot.ClipSlotSynchronizer import ClipSlotSynchronizer
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from a_protocol_0.lom.track.group_track.ExternalSynthTrackName import ExternalSynthTrackName
from a_protocol_0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.simple_track.TrackSynchronizer import TrackSynchronizer


class ExternalSynthTrack(ExternalSynthTrackActionMixin, AbstractGroupTrack):
    def __init__(self, base_group_track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(ExternalSynthTrack, self).__init__(base_group_track=base_group_track, *a, **k)
        self.midi_track = base_group_track.sub_tracks[0]
        self.audio_track = base_group_track.sub_tracks[1]
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

        # audio and midi tracks are now handled by self
        self.audio_track.abstract_group_track = self
        self.midi_track.abstract_group_track = self

        self.track_name.disconnect()  # type: ignore[has-type]
        self.track_name = ExternalSynthTrackName(self)

        self.audio_track.set_output_routing_to(self.base_track)

        # the instrument handling relies on the group track
        # noinspection PyUnresolvedReferences
        self.notify_instrument()

    @property
    def instrument(self):
        # type: () -> AbstractInstrument
        return cast(AbstractInstrument, self.midi_track.instrument)

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
        self._midi_track_synchronizer.disconnect()
        self._midi_audio_synchronizer.disconnect()
        for clip_slot_synchronizer in self._clip_slot_synchronizers:
            clip_slot_synchronizer.disconnect()

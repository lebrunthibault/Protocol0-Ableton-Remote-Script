from typing import TYPE_CHECKING, Any

from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class ExternalSynthTrack(ExternalSynthTrackActionMixin, AbstractTrack):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(ExternalSynthTrack, self).__init__(track=track._track, *a, **k)
        self.base_track = track
        self.group_track = self.base_track.group_track
        self.group_tracks = self.base_track.group_track
        self.sub_tracks = self.base_track.sub_tracks
        self.midi = self.sub_tracks[0]
        self.audio = self.sub_tracks[1]
        self.selectable_track = self.midi
        self.can_be_armed = True
        if not self.arm:
            self.is_folded = True

        self.instrument = self.selectable_track.instrument

    @property
    def arm(self):
        # type: () -> bool
        return all([sub_track.arm for sub_track in self.sub_tracks])

    @property
    def is_playing(self):
        # type: () -> bool
        return any([sub_track.is_playing for sub_track in self.sub_tracks])

    @property
    def is_recording(self):
        # type: () -> bool
        return any([sub_track.is_recording for sub_track in self.sub_tracks])

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> ClipSlot
        for i in range(len(self.song.scenes)):
            if not self.midi.clip_slots[i].has_clip and not self.audio.clip_slots[i].has_clip:
                return i
        self.song.create_scene()
        return len(self.song.scenes) - 1

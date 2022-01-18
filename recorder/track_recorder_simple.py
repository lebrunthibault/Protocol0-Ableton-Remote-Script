from typing import Optional

from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface
from protocol0.sequence.Sequence import Sequence


class TrackRecorderSimple(TrackRecorderInterface):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        super(TrackRecorderSimple, self).__init__(track=track)
        self.track = track

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        for i in range(self.song.selected_scene.index, len(self.song.scenes)):
            if not self.track.clip_slots[i].clip:
                return i

        return None

    def _focus_empty_clip_slot(self):
        # type: () -> Sequence
        seq = Sequence()
        if self.next_empty_clip_slot_index is None:
            seq.add(self.song.create_scene)
            seq.add(self.track.arm_track)
        elif self.next_empty_clip_slot_index != self.song.selected_scene.index:
            seq.add(self.song.scenes[self.next_empty_clip_slot_index].select)

        return seq.done()

    def record(self, bar_length):
        # type: (int) -> Sequence
        recording_clip_slot = self.track.clip_slots[self.next_empty_clip_slot_index]
        return recording_clip_slot.record(bar_length=bar_length)

    def on_record_cancelled(self):
        # type: () -> Sequence
        return self.track.playable_clip_slot.delete_clip()

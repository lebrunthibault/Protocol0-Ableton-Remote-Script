from protocol0.recorder.track_recorder_decorator.track_recorder_decorator import TrackRecorderDecorator
from protocol0.sequence.Sequence import Sequence


class TrackRecorderFocusEmptyClipSlotDecorator(TrackRecorderDecorator):
    def pre_record(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self._focus_empty_clip_slot)
        seq.add(super(TrackRecorderFocusEmptyClipSlotDecorator, self).pre_record)
        return seq.done()

    def _focus_empty_clip_slot(self):
        # type: () -> Sequence
        seq = Sequence()
        if self.next_empty_clip_slot_index is None:
            seq.add(self.song.create_scene)
        elif self.next_empty_clip_slot_index != self.song.selected_scene.index:
            seq.add(self.song.scenes[self.next_empty_clip_slot_index].select)

        return seq.done()

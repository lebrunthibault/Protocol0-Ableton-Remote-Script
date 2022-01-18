from functools import partial

from protocol0.recorder.decorators.track_recorder_decorator import TrackRecorderDecorator
from protocol0.sequence.Sequence import Sequence


class TrackRecorderCountInOneBarDecorator(TrackRecorderDecorator):
    def pre_record(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self._launch_count_in)
        seq.add(super(TrackRecorderCountInOneBarDecorator, self).pre_record)
        return seq.done()

    def _launch_count_in(self):
        # type: () -> Sequence
        self.song.metronome = True
        self.song.stop_playing()
        self.song.stop_all_clips(quantized=False)  # stopping previous scene clips
        # solo for count in
        self.solo = True
        self.song.is_playing = True
        self.parent.wait_bars(1, partial(setattr, self, "solo", False))
        seq = Sequence()
        return seq.done()

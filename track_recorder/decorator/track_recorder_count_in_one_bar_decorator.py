from functools import partial

from protocol0.track_recorder.decorator.track_recorder_decorator import TrackRecorderDecorator
from protocol0.sequence.Sequence import Sequence


class TrackRecorderCountInOneBarDecorator(TrackRecorderDecorator):
    def pre_record(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self.recorder.pre_record)
        seq.add(self._launch_count_in)
        seq.add(self._stop_count_in)
        return seq.done()

    def _launch_count_in(self):
        # type: () -> Sequence
        self.song.metronome = True
        self.song.stop_playing()
        self.song.stop_all_clips(quantized=False)  # stopping previous scene clips
        # solo for count in
        self.solo = True
        self.song.is_playing = True
        seq = Sequence()
        seq.add(wait_bars=1)
        seq.add(partial(setattr, self, "solo", False))
        return seq.done()

    def _stop_count_in(self):
        # type: () -> None
        if len(list(filter(None, [t.is_hearable for t in self.song.abstract_tracks]))) > 1:
            self.song.metronome = False

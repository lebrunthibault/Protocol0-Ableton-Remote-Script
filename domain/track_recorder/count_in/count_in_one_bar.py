from functools import partial

from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface


class CountInOneBar(CountInInterface):
    def launch(self):
        # type: () -> Sequence
        self.song.metronome = True
        self.song.stop_playing()
        self.song.stop_all_clips(quantized=False)  # stopping previous scene clips
        # solo for count in
        self.track.solo = True
        self.song.is_playing = True
        seq = Sequence()
        seq.add(wait_bars=1)
        seq.add(partial(setattr, self.track, "solo", False))
        seq.add(self._stop_count_in)
        return seq.done()

    def _stop_count_in(self):
        # type: () -> None
        if len(list(filter(None, [t.is_hearable for t in self.song.abstract_tracks]))) > 1:
            self.song.metronome = False

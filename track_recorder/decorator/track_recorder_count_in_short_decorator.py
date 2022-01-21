from protocol0.track_recorder.decorator.track_recorder_decorator import TrackRecorderDecorator
from protocol0.sequence.Sequence import Sequence


class TrackRecorderCountInShortDecorator(TrackRecorderDecorator):
    def _pre_record(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self._launch_count_in)
        seq.add(super(TrackRecorderCountInShortDecorator, self).pre_record)
        return seq.done()

    def _launch_count_in(self):
        # type: () -> Sequence
        self.song.stop_playing
        self.track.stop(immediate=True)
        seq = Sequence()
        seq.add(wait=40)  # mini count in
        return seq.done()

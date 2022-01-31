from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface


class CountInShort(CountInInterface):
    def launch(self):
        # type: () -> Sequence
        self.song.stop_playing()
        # self.track.stop(immediate=True)
        seq = Sequence()
        seq.add(wait=40)  # mini count in
        return seq.done()

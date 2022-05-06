from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.shared.sequence.Sequence import Sequence


class CountInShort(CountInInterface):
    def launch(self):
        # type: () -> Sequence
        self._playback_component.stop_playing()
        # self.track.stop(immediate=True)
        seq = Sequence()
        seq.wait(40)  # mini count in
        return seq.done()

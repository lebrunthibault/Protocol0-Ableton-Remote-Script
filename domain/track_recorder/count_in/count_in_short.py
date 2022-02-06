from protocol0.domain.lom.song.Song import Song
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface


class CountInShort(CountInInterface):
    def launch(self):
        # type: () -> Sequence
        Song.get_instance().stop_playing()
        # self.track.stop(immediate=True)
        seq = Sequence()
        seq.add(wait=40)  # mini count in
        return seq.done()

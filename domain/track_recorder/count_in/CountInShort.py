from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.shared.sequence.Sequence import Sequence


class CountInShort(CountInInterface):
    def launch(self, playback_component, _):
        # type: (PlaybackComponent, AbstractTrack) -> Sequence
        playback_component.stop_playing()
        # self.track.stop(immediate=True)
        seq = Sequence()
        seq.wait(40)  # mini count in
        return seq.done()

from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.shared.sequence.Sequence import Sequence


class CountInInterface(object):
    def launch(self, playback_component, track):
        # type: (PlaybackComponent, AbstractTrack) -> Sequence
        raise NotImplementedError

from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.shared.sequence.Sequence import Sequence


class CountInInterface(object):
    def __init__(self, track, playback_component):
        # type: (AbstractTrack, PlaybackComponent) -> None
        super(CountInInterface, self).__init__()
        self._track = track
        self._playback_component = playback_component

    def launch(self):
        # type: () -> Sequence
        raise NotImplementedError

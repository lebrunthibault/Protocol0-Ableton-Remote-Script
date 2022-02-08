from typing import TYPE_CHECKING

from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class CountInInterface(object):
    def __init__(self, track, song):
        # type: (AbstractTrack, Song) -> None
        super(CountInInterface, self).__init__()
        self.track = track
        self._song = song

    def launch(self):
        # type: () -> Sequence
        raise NotImplementedError

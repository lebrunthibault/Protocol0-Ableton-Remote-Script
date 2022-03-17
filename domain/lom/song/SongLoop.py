from typing import TYPE_CHECKING

from protocol0.domain.lom.loop.LoopableInterface import LoopableInterface

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class SongLoop(LoopableInterface):
    """ handle start / end markers and loop gracefully """
    def __init__(self, song):
        # type: (Song) -> None
        self._song = song

    def __repr__(self):
        # type: () -> str
        return "SongLoop(%s)" % self._song

    @property
    def looping(self):
        # type: () -> bool
        return self._song.looping

    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        self._song.looping = looping

    @property
    def start(self):
        # type: () -> float
        return self._song.loop_start

    @start.setter
    def start(self, start):
        # type: (float) -> None
        loop_length = self.end - start
        self._song.loop_start = start
        self.length = loop_length

    @property
    def end(self):
        # type: () -> float
        return self.start + self.length

    @end.setter
    def end(self, end):
        # type: (float) -> None
        self.length = end - self.start

    @property
    def length(self):
        # type: () -> float
        return self._song.loop_length

    @length.setter
    def length(self, length):
        # type: (float) -> None
        self._song.loop_length = length

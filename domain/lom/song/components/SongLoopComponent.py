import Live

from protocol0.domain.lom.loop.LoopableInterface import LoopableInterface


class SongLoopComponent(LoopableInterface):
    """ handle start / end markers and loop gracefully """

    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        self._live_song = song

    def __repr__(self):
        # type: () -> str
        return "SongLoop"

    @property
    def looping(self):
        # type: () -> bool
        return self._live_song.loop

    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        self._live_song.loop = looping

    @property
    def start(self):
        # type: () -> float
        return self._live_song.loop_start

    @start.setter
    def start(self, start):
        # type: (float) -> None
        loop_length = self.end - start
        self._live_song.loop_start = start
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
        return self._live_song.loop_length

    @length.setter
    def length(self, length):
        # type: (float) -> None
        self._live_song.loop_length = length

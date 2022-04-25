from typing import TYPE_CHECKING

from protocol0.domain.lom.loop.LoopableInterface import LoopableInterface

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipLoop(LoopableInterface):
    """ handle start / end markers and loop gracefully """

    def __init__(self, clip):
        # type: (Clip) -> None
        self._clip = clip

    def __repr__(self):
        # type: () -> str
        return "ClipLoop(%s)" % self._clip

    @property
    def looping(self):
        # type: () -> bool
        return self._clip.looping

    @looping.setter
    def looping(self, looping):
        # type: (bool) -> None
        self._clip.looping = looping

    @property
    def start(self):
        # type: () -> float
        return self._clip.loop_start

    @start.setter
    def start(self, start):
        # type: (float) -> None
        self._clip.start_marker = start
        self._clip.loop_start = start

    @property
    def end(self):
        # type: () -> float
        return self._clip.loop_end

    @end.setter
    def end(self, end):
        # type: (float) -> None
        self._clip.end_marker = end
        self._clip.loop_end = end

    @property
    def length(self):
        # type: () -> float
        return self._clip.length

    @length.setter
    def length(self, length):
        # type: (float) -> None
        self._clip.length = length

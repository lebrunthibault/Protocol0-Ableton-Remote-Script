from typing import TYPE_CHECKING

from protocol0.domain.shared.System import System
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipLoop(object):
    """ handle start / end markers and loop gracefully """
    def __init__(self, clip):
        # type: (Clip) -> None
        self._clip = clip

    @property
    def start(self):
        # type: () -> float
        return self._clip.start_marker

    @start.setter
    def start(self, start):
        # type: (float) -> None
        assert start >= 0, "start should be >= 0"
        if start % SongFacade.signature_numerator() != 0:
            System.client().show_warning("start should be a bar length")
            return
        if start >= self._clip.end_marker:
            System.client().show_warning("Cannot set start >= end_marker")
            return
        if start >= self._clip.loop_end:
            System.client().show_warning("Cannot set start >= loop_end")
            return

        self._clip.start_marker = start
        self._clip.loop_start = start

    def scroll_start(self, go_next):
        # type: (bool) -> None
        factor = 1 if go_next else -1
        start = self.start + (factor * SongFacade.signature_numerator())
        if start >= self.end or start < 0:
            return
        self.start = start

    @property
    def end(self):
        # type: () -> float
        return self._clip.end_marker

    @end.setter
    def end(self, end):
        # type: (float) -> None
        if end > self._clip.length:
            System.client().show_warning("end should be <= length")
            return
        if end % SongFacade.signature_numerator() != 0:
            System.client().show_warning("end should be a bar length")
            return
        if end <= self._clip.start_marker:
            System.client().show_warning("Cannot set end <= start_marker")
            return
        if end <= self._clip.loop_start:
            System.client().show_warning("Cannot set end <= loop_start")
            return

        self._clip.end_marker = end
        self._clip.loop_end = end

    def scroll_end(self, go_next):
        # type: (bool) -> None
        factor = 1 if go_next else -1
        end = self.end + (factor * SongFacade.signature_numerator())
        Logger.log_dev("end is %s" % end)
        if end <= self.start or end > self._clip.length:
            Logger.log_dev("end not valid")
            return
        self.end = end

from typing import TYPE_CHECKING

from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipPlayingPosition(object):
    def __init__(self, clip):
        # type: (Clip) -> None
        self._clip = clip

    def __repr__(self):
        # type: () -> str
        return "position: %s, bar_position: %s, current_bar: %s, in_last_bar: %s" % (
            self.position, self.bar_position, self.current_bar, self.in_last_bar
        )

    @property
    def position(self):
        # type: () -> float
        return self._clip._clip.playing_position - self._clip.start_marker

    @property
    def bar_position(self):
        # type: () -> float
        return self.position / SongFacade.signature_numerator()

    @property
    def current_bar(self):
        # type: () -> int
        if self._clip.length == 0:
            return 0
        return int(self.bar_position)

    @property
    def in_last_bar(self):
        # type: () -> bool
        return self.current_bar == self._clip.bar_length - 1

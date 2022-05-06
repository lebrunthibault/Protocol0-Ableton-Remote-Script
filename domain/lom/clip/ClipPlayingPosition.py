import Live

from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.shared.SongFacade import SongFacade


class ClipPlayingPosition(object):
    def __init__(self, live_clip, clip_loop):
        # type: (Live.Clip.Clip, ClipLoop) -> None
        self._live_clip = live_clip
        self._clip_loop = clip_loop

    def __repr__(self):
        # type: () -> str
        return "position: %s, bar_position: %s, current_bar: %s, in_last_bar: %s" % (
            self.position, self.bar_position, self.current_bar, self.in_last_bar
        )

    @property
    def position(self):
        # type: () -> float
        return self._live_clip.playing_position - self._clip_loop.start

    @property
    def bar_position(self):
        # type: () -> float
        return self.position / SongFacade.signature_numerator()

    @property
    def current_bar(self):
        # type: () -> int
        if self._clip_loop.length == 0:
            return 0
        return int(self.bar_position)

    @property
    def in_last_bar(self):
        # type: () -> bool
        return self.current_bar == self._clip_loop.bar_length - 1

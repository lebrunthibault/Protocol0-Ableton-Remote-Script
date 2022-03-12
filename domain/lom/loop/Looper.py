from protocol0.domain.lom.loop.LoopableInterface import LoopableInterface
from protocol0.shared.SongFacade import SongFacade


class Looper(object):
    def __init__(self, obj):
        # type: (LoopableInterface) -> None
        self._obj = obj

    def scroll_start(self, go_next):
        # type: (bool) -> None
        self._obj.looping = True
        factor = 1 if go_next else -1
        start = self._obj.start + (factor * SongFacade.signature_numerator())
        if start >= self._obj.end or start < 0:
            return
        self._obj.start = start

    def scroll_end(self, go_next):
        # type: (bool) -> None
        self._obj.looping = True
        factor = 1 if go_next else -1
        end = self._obj.end + (factor * SongFacade.signature_numerator())
        if end <= self._obj.start:
            return
        self._obj.end = end

    def scroll_loop(self, go_next):
        # type: (bool) -> None
        self._obj.looping = True
        factor = 1 if go_next else -1
        start = self._obj.start + (factor * SongFacade.signature_numerator())
        end = self._obj.end + (factor * SongFacade.signature_numerator())
        if start < 0:
            return

        self._obj.start = start
        self._obj.end = end

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class SongViewFacade(object):
    _INSTANCE = None  # type: Optional[SongViewFacade]

    def __init__(self, song):
        # type: (Song) -> None
        SongViewFacade._INSTANCE = self
        self._song = song

    @classmethod
    def draw_mode(cls, draw_mode):
        # type: (bool) -> None
        cls._INSTANCE._song.draw_mode = draw_mode

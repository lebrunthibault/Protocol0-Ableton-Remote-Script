from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class AccessSong(object):
    """ Providing global access to the song object (should be limited) """

    @property
    def _song(self):
        # type: () -> Song
        from protocol0.application.Protocol0 import Protocol0

        return Protocol0.CONTAINER.song

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song  # noqa
    from protocol0.application.Protocol0 import Protocol0  # noqa


class AccessSong(object):
    """ Providing global access to the song object (should be limited) """

    @property
    def song(self):
        # type: () -> Song
        from protocol0.domain.lom.song.Song import Song  # noqa

        return Song.get_instance()

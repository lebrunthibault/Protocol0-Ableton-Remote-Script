from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song
    from protocol0.application.Protocol0 import Protocol0


class AccessGlobalState(object):
    """ Providing global access to services (should be changed) """

    @property
    def parent(self):
        # type: () -> Protocol0
        from protocol0 import Protocol0

        return Protocol0.SELF

    @property
    def song(self):
        # type: () -> Song
        from protocol0.domain.lom.song.Song import Song

        return Song.get_instance()

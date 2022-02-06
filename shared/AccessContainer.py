from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song  # noqa
    from protocol0.application.Protocol0 import Protocol0  # noqa


class AccessContainer(object):
    """ Providing global access to the container (should be changed by using dependency injection) """

    @property
    def parent(self):
        # type: () -> Protocol0
        from protocol0 import Protocol0  # noqa

        return Protocol0.SELF

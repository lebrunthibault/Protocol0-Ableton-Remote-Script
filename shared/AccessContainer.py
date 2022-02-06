from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from protocol0.application.Container import Container


class AccessContainer(object):
    """ Provides global access to the container (should be changed by using DI everywhere) """

    @property
    def container(self):
        # type: () -> Container
        from protocol0 import Protocol0  # noqa

        return Protocol0.CONTAINER

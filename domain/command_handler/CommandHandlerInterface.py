from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.application.Container import Container


class CommandHandlerInterface(object):
    def __init__(self, container):
        # type: (Container) -> None
        self._container = container

    def handle(self, message):
        # type: (Any) -> None
        raise NotImplementedError

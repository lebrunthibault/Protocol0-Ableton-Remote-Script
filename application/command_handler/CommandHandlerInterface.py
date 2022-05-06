from typing import Any, Optional

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.shared.sequence.Sequence import Sequence


class CommandHandlerInterface(object):
    def __init__(self, container):
        # type: (ContainerInterface) -> None
        self._container = container

    def handle(self, message):
        # type: (Any) -> Optional[Sequence]
        raise NotImplementedError

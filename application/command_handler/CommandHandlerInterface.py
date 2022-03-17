from typing import Any, TYPE_CHECKING, Optional

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class CommandHandlerInterface(object):
    def __init__(self, container, song):
        # type: (ContainerInterface, Song) -> None
        self._container = container
        self._song = song

    def handle(self, message):
        # type: (Any) -> Optional[Sequence]
        raise NotImplementedError

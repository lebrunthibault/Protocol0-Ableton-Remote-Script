from typing import Any


class CommandHandlerInterface(object):
    def handle(self, message):
        # type: (Any) -> None
        raise NotImplementedError

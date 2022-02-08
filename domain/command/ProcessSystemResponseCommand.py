from typing import Any

from protocol0.domain.command.SerializableCommand import SerializableCommand


class ProcessSystemResponseCommand(SerializableCommand):
    def __init__(self, res):
        # type: (Any) -> None
        self.res = res

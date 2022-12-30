from typing import Any

from protocol0.application.command.SerializableCommand import SerializableCommand


class EmitBackendEventCommand(SerializableCommand):
    def __init__(self, event, data=None):
        # type: (str, Any) -> None
        super(EmitBackendEventCommand, self).__init__()
        self.event = event
        self.data = data

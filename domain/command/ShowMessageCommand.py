from protocol0.domain.command.SerializableCommand import SerializableCommand


class ShowMessageCommand(SerializableCommand):
    def __init__(self, message):
        # type: (str) -> None
        self.message = message

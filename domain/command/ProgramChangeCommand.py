from protocol0.domain.command.SerializableCommand import SerializableCommand


class ProgramChangeCommand(SerializableCommand):
    def __init__(self, value):
        # type: (int) -> None
        self.value = value

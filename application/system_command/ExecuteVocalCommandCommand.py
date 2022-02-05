from protocol0.application.system_command.SerializableCommand import SerializableCommand


class ExecuteVocalCommandCommand(SerializableCommand):
    def __init__(self, command):
        # type: (str) -> None
        self.command = command

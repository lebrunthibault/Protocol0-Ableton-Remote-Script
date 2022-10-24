from protocol0.application.command.SerializableCommand import SerializableCommand


class EnableScriptCommand(SerializableCommand):
    def __init__(self, enabled):
        # type: (bool) -> None
        super(EnableScriptCommand, self).__init__()
        self.enabled = enabled

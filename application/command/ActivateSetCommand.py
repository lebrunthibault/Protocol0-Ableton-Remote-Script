from protocol0.application.command.SerializableCommand import SerializableCommand


class ActivateSetCommand(SerializableCommand):
    def __init__(self, active):
        # type: (bool) -> None
        super(ActivateSetCommand, self).__init__()
        self.active = active

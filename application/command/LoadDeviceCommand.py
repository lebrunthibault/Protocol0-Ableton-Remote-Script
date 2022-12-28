from protocol0.application.command.SerializableCommand import SerializableCommand


class LoadDeviceCommand(SerializableCommand):
    def __init__(self, enum_name):
        # type: (str) -> None
        super(LoadDeviceCommand, self).__init__()
        self.enum_name = enum_name

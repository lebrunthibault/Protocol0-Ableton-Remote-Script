from protocol0.application.command.SerializableCommand import SerializableCommand


class LoadDeviceCommand(SerializableCommand):
    def __init__(self, device_name):
        # type: (str) -> None
        self.device_name = device_name

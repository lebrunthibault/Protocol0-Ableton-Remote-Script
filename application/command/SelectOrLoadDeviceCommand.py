from protocol0.application.command.SerializableCommand import SerializableCommand


class SelectOrLoadDeviceCommand(SerializableCommand):
    def __init__(self, device_name):
        # type: (str) -> None
        self.device_name = device_name

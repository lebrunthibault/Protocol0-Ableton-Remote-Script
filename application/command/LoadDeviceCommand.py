from protocol0.application.command.SerializableCommand import SerializableCommand


class LoadDeviceCommand(SerializableCommand):
    def __init__(self, device_name, on_selected_track=False):
        # type: (str, bool) -> None
        self.device_name = device_name
        self.on_selected_track = on_selected_track

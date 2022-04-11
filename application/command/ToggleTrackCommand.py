from protocol0.application.command.SerializableCommand import SerializableCommand


class ToggleTrackCommand(SerializableCommand):
    def __init__(self, track_name):
        # type: (str) -> None
        self.track_name = track_name
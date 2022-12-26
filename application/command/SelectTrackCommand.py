from protocol0.application.command.SerializableCommand import SerializableCommand


class SelectTrackCommand(SerializableCommand):
    def __init__(self, track_name):
        # type: (str) -> None
        super(SelectTrackCommand, self).__init__()
        self.track_name = track_name
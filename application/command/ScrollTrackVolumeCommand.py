from protocol0.application.command.SerializableCommand import SerializableCommand


class ScrollTrackVolumeCommand(SerializableCommand):
    def __init__(self, go_next=False):
        # type: (bool) -> None
        self.go_next = go_next

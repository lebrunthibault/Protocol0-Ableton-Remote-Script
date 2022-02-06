from protocol0.application.command.SerializableCommand import SerializableCommand


class SearchTrackCommand(SerializableCommand):
    def __init__(self, search):
        # type: (str) -> None
        self.search = search

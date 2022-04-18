from protocol0.application.command.SerializableCommand import SerializableCommand


class LoadDrumRackCommand(SerializableCommand):
    def __init__(self, drum_name):
        # type: (str) -> None
        self.drum_name = drum_name

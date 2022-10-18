from protocol0.application.command.SerializableCommand import SerializableCommand


class ScrollScenesCommand(SerializableCommand):
    def __init__(self, go_next=False):
        # type: (bool) -> None
        super(ScrollScenesCommand, self).__init__()
        self.go_next = go_next

from protocol0.application.command.SerializableCommand import SerializableCommand


class ScrollScenePositionCommand(SerializableCommand):
    def __init__(self, go_next=False, use_fine_scrolling=False):
        # type: (bool, bool) -> None
        """
            go_next == True: go right
            use_fine_scrolling True: scroll by beat instead of bars
        """
        super(ScrollScenePositionCommand, self).__init__()
        self.go_next = go_next
        self.use_fine_scrolling = use_fine_scrolling

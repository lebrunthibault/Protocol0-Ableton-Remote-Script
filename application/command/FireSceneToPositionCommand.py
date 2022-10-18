from typing import Optional

from protocol0.application.command.SerializableCommand import SerializableCommand


class FireSceneToPositionCommand(SerializableCommand):
    def __init__(self, bar_length=None):
        # type:  (Optional[int]) -> None
        super(FireSceneToPositionCommand, self).__init__()
        self.bar_length = bar_length

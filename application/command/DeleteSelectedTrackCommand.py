from typing import Optional

from protocol0.application.command.SerializableCommand import SerializableCommand


class DeleteSelectedTrackCommand(SerializableCommand):
    def __init__(self, track_name=None):
        # type:  (Optional[str]) -> None
        super(DeleteSelectedTrackCommand, self).__init__()
        self.track_name = track_name

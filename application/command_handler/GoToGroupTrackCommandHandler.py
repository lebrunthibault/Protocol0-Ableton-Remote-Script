from protocol0.application.command.GoToGroupTrackCommand import GoToGroupTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.TrackService import TrackService


class GoToGroupTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (GoToGroupTrackCommand) -> None
        self._container.get(TrackService).go_to_group_track()

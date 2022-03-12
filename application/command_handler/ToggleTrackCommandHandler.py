from protocol0.application.command.ToggleTrackCommand import ToggleTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.TrackPlayerService import TrackPlayerService


class ToggleTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ToggleTrackCommand) -> None
        self._container.get(TrackPlayerService).toggle_track(command.track_name)

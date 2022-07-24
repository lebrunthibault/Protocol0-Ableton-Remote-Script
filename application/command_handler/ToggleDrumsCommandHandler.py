from protocol0.application.command.ToggleDrumsCommand import ToggleDrumsCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.TrackPlayerService import TrackPlayerService


class ToggleDrumsCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ToggleDrumsCommand) -> None
        self._container.get(TrackPlayerService).toggle_drums()

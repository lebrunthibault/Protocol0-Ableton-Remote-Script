from protocol0.application.command.ResetSongCommand import ResetSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.infra.persistence.SongDataService import SongDataService


class ResetSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ResetSongCommand) -> None
        self._song.reset()
        self._container.get(SongDataService).save()

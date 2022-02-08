from protocol0.application.command.SaveSongDataCommand import SaveSongDataCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.infra.persistence.SongDataService import SongDataService


class SaveSongDataCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (SaveSongDataCommand) -> None
        self._container.get(SongDataService).save()

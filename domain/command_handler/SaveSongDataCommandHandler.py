from protocol0.domain.command.SaveSongDataCommand import SaveSongDataCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.SongDataServiceInterface import SongDataServiceInterface


class SaveSongDataCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (SaveSongDataCommand) -> None
        self._container.get(SongDataServiceInterface).save()

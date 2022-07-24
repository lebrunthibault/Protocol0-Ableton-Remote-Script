from protocol0.application.command.GetSongStateCommand import GetSongStateCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.SongState import SongState


class GetSongStateCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (GetSongStateCommand) -> None
        self._container.get(SongState).notify(force=True)

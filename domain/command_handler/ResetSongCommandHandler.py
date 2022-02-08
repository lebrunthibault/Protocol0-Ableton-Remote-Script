from protocol0.domain.command.ResetSongCommand import ResetSongCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface


class ResetSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ResetSongCommand) -> None
        self._song.reset()

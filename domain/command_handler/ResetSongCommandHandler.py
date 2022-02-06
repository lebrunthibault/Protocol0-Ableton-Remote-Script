from protocol0.application.command.ResetSongCommand import ResetSongCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.AccessSong import AccessSong


class ResetSongCommandHandler(CommandHandlerInterface, AccessSong):
    def handle(self, command):
        # type: (ResetSongCommand) -> None
        self._song.reset(save_data=True)

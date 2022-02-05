from protocol0.application.system_command.ResetSongCommand import ResetSongCommand
from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.Song import Song


class ResetSongCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ResetSongCommand) -> None
        Song.get_instance().reset(save_data=True)

from protocol0.application.command.PlayPauseCommand import PlayPauseCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface


class PlayPauseCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (PlayPauseCommand) -> None
        self._song.play_pause()

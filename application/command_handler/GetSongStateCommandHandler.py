from protocol0.application.command.GetSongStateCommand import GetSongStateCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface


class GetSongStateCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (GetSongStateCommand) -> None
        self._song.state.notify()

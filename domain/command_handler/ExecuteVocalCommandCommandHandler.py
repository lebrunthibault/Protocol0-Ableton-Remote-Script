from protocol0.application.vocal_command.VocalCommandService import VocalCommandService
from protocol0.domain.command.ExecuteVocalCommandCommand import ExecuteVocalCommandCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface


class ExecuteVocalCommandCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ExecuteVocalCommandCommand) -> None
        self._container.get(VocalCommandService).execute_command(command.command)

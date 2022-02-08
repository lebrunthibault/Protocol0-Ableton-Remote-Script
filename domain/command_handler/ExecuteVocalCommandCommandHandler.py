from protocol0.application.vocal_command.VocalCommandManager import VocalCommandManager
from protocol0.domain.command.ExecuteVocalCommandCommand import ExecuteVocalCommandCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface


class ExecuteVocalCommandCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ExecuteVocalCommandCommand) -> None
        self._container.get(VocalCommandManager).execute_command(command.command)

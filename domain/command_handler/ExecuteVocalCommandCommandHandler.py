from protocol0.application.command.ExecuteVocalCommandCommand import ExecuteVocalCommandCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface


class ExecuteVocalCommandCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ExecuteVocalCommandCommand) -> None
        self._container.vocal_command_manager.execute_command(command.command)

from protocol0.application.system_command.ExecuteVocalCommandCommand import ExecuteVocalCommandCommand
from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface


class ExecuteVocalCommandCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ExecuteVocalCommandCommand) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.vocalCommandManager.execute_command(command.command)


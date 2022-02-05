from protocol0.application.system_command.ClearLogsCommand import ClearLogsCommand
from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface


class ClearLogsCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ClearLogsCommand) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.logManager.clear()

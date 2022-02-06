from protocol0.application.command.ClearLogsCommand import ClearLogsCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.AccessContainer import AccessContainer
from protocol0.shared.Logger import Logger


class ClearLogsCommandHandler(CommandHandlerInterface, AccessContainer):
    def handle(self, command):
        # type: (ClearLogsCommand) -> None
        Logger.clear()

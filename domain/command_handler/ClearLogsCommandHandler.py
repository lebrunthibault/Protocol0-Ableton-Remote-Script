from protocol0.domain.command.ClearLogsCommand import ClearLogsCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Logger import Logger


class ClearLogsCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ClearLogsCommand) -> None
        Logger.clear()

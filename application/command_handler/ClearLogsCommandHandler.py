from protocol0.application.command.ClearLogsCommand import ClearLogsCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.logging.Logger import Logger


class ClearLogsCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ClearLogsCommand) -> None
        Logger.clear()

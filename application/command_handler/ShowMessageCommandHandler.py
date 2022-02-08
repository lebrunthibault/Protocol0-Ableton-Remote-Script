from protocol0.application.command.ShowMessageCommand import ShowMessageCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.logging.StatusBar import StatusBar


class ShowMessageCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ShowMessageCommand) -> None
        StatusBar.show_message(command.message)

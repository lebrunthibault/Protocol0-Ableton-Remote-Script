from protocol0.application.system_command.ShowMessageCommand import ShowMessageCommand
from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.StatusBar import StatusBar


class ShowMessageCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ShowMessageCommand) -> None
        StatusBar.show_message(command.message)

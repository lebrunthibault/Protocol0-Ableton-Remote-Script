from protocol0.application.command.ProcessSystemResponseCommand import ProcessSystemResponseCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.sequence.Sequence import Sequence


class ProcessSystemResponseCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProcessSystemResponseCommand) -> None

        Sequence.handle_system_response(command.res)

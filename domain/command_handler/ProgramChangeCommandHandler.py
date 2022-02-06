from protocol0.application.command.ProgramChangeCommand import ProgramChangeCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface


class ProgramChangeCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProgramChangeCommand) -> None
        self._container.midi_manager.send_program_change(command.value)

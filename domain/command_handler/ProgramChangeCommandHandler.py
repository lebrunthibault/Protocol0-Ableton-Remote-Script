from protocol0.domain.command.ProgramChangeCommand import ProgramChangeCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.midi.MidiServiceInterface import MidiServiceInterface


class ProgramChangeCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProgramChangeCommand) -> None
        self._container.get(MidiServiceInterface).send_program_change(command.value)

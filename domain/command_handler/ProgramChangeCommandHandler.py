from protocol0.domain.command.ProgramChangeCommand import ProgramChangeCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.midi.MidiManagerInterface import MidiManagerInterface


class ProgramChangeCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProgramChangeCommand) -> None
        self._container.get(MidiManagerInterface).send_program_change(command.value)

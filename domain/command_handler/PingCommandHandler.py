from protocol0.domain.command.PingCommand import PingCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.midi.MidiManagerInterface import MidiManagerInterface


class PingCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (PingCommand) -> None
        """ Called by the backend when the system midi_api ping is called """
        self._container.get(MidiManagerInterface).pong_from_midi_server()

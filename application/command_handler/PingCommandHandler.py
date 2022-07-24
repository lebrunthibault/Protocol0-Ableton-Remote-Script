from protocol0.application.command.PingCommand import PingCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.infra.midi.MidiService import MidiService


class PingCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (PingCommand) -> None
        """Called by the backend when the backend as a response to the midi_api ping"""
        self._container.get(MidiService).pong_from_midi_server()

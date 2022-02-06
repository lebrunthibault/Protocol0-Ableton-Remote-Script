from protocol0.application.command.PingCommand import PingCommand
from protocol0.domain.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.AccessContainer import AccessContainer
from protocol0.shared.Logger import Logger


class PingCommandHandler(CommandHandlerInterface, AccessContainer):
    def handle(self, command):
        # type: (PingCommand) -> None
        """ Called by the backend when the system midi_api ping is called """

        Logger.clear()
        if self._container.midi_manager.midi_server_check_timeout_scheduler_event:
            self._container.midi_manager.midi_server_check_timeout_scheduler_event.cancel()

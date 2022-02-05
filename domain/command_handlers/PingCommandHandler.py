from protocol0 import Protocol0
from protocol0.application.system_command.PingCommand import PingCommand
from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Logger import Logger


class PingCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (PingCommand) -> None
        """ Called by the backend when the system midi_api ping is called """
        Protocol0.SELF.logManager.clear()
        Logger.log_info("Midi server is running")
        if Protocol0.SELF.midi_server_check_timeout_scheduler_event:
            Protocol0.SELF.midi_server_check_timeout_scheduler_event.cancel()

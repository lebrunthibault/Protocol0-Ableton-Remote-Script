from protocol0.application.system_command.PingCommand import PingCommand
from protocol0.domain.command_handlers.CommandHandlerInterface import CommandHandlerInterface


class PingCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (PingCommand) -> None
        """ Called by the backend when the system midi_api ping is called """
        from protocol0 import Protocol0

        Protocol0.SELF.logManager.clear()
        if Protocol0.SELF.midi_server_check_timeout_scheduler_event:
            Protocol0.SELF.midi_server_check_timeout_scheduler_event.cancel()

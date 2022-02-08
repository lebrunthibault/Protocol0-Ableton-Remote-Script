from protocol0.application.command.ProcessSystemResponseCommand import ProcessSystemResponseCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.shared.logging.Logger import Logger


class ProcessSystemResponseCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProcessSystemResponseCommand) -> None
        waiting_sequence = next((seq for seq in Sequence.RUNNING_SEQUENCES if seq.waiting_for_system), None)
        if waiting_sequence is None:
            Logger.log_info("Response (%s) received from system but couldn't find a waiting sequence" % command.res)
            return

        waiting_sequence.on_system_response(res=command.res)

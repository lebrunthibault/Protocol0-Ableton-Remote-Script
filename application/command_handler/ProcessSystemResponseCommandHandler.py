from protocol0.application.command.ProcessSystemResponseCommand import ProcessSystemResponseCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.BackendResponseEvent import BackendResponseEvent


class ProcessSystemResponseCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProcessSystemResponseCommand) -> None
        DomainEventBus.notify(BackendResponseEvent(command.res))

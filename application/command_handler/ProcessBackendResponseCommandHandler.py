from protocol0.application.command.ProcessBackendResponseCommand import ProcessBackendResponseCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.backend.BackendResponseEvent import BackendResponseEvent


class ProcessBackendResponseCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProcessBackendResponseCommand) -> None
        DomainEventBus.notify(BackendResponseEvent(command.res))

from protocol0.application.command.ProcessBackendResponseCommand import ProcessBackendResponseCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.backend.BackendResponseEvent import BackendResponseEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ProcessBackendResponseCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ProcessBackendResponseCommand) -> None
        DomainEventBus.emit(BackendResponseEvent(command.res))

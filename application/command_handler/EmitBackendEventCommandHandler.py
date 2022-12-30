from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.backend.BackendEvent import BackendEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class EmitBackendEventCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (EmitBackendEventCommand) -> None
        DomainEventBus.emit(BackendEvent(command.event, command.data))

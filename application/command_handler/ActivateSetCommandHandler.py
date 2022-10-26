from protocol0.application.command.ActivateSetCommand import ActivateSetCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.song.SongInitService import SongInitService
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.lom.set.AbletonSetChangedEvent import AbletonSetChangedEvent


class ActivateSetCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ActivateSetCommand) -> None
        ableton_set = self._container.get(AbletonSet)
        ableton_set.active = command.active

        DomainEventBus.emit(AbletonSetChangedEvent(ableton_set))
        if not command.active:
            self._container.get(SongInitService).init_song()

from protocol0.application.command.EnableScriptCommand import EnableScriptCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.SongInitService import SongInitService
from protocol0.domain.lom.song.AbletonSet import AbletonSet
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.script.ScriptStateChangedEvent import ScriptStateChangedEvent
from protocol0.domain.shared.script.ScriptStateService import ScriptStateService


class EnableScriptCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (EnableScriptCommand) -> None
        self._container.get(ScriptStateService).enabled = command.enabled
        DomainEventBus.emit(ScriptStateChangedEvent(command.enabled))
        if not command.enabled:
            self._container.get(SongInitService).init_song()
        self._container.get(AbletonSet).notify(force=True)

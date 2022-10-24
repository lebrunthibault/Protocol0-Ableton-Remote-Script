from protocol0.application.command.EnableScriptCommand import EnableScriptCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.SongState import SongState
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.script.ScriptStateChangedEvent import ScriptStateChangedEvent
from protocol0.domain.shared.script.ScriptStateService import ScriptStateService


class EnableScriptCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (EnableScriptCommand) -> None
        self._container.get(ScriptStateService).enabled = command.enabled
        DomainEventBus.emit(ScriptStateChangedEvent(command.enabled))
        self._container.get(SongState).notify(force=True)

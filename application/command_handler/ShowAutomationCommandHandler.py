from protocol0.application.command.ShowAutomationCommand import ShowAutomationCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.TrackAutomationService import TrackAutomationService


class ShowAutomationCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ShowAutomationCommand) -> None
        self._container.get(TrackAutomationService).show_automation(command.go_next)

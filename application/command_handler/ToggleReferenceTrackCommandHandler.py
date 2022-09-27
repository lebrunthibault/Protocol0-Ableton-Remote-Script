from protocol0.application.command.ToggleReferenceTrackCommand import ToggleReferenceTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ToggleReferenceTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ToggleReferenceTrackCommand) -> None
        SongFacade.reference_track().toggle()

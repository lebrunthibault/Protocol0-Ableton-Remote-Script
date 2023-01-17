from protocol0.application.command.ToggleReferenceTrackCommand import ToggleReferenceTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ToggleReferenceTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ToggleReferenceTrackCommand) -> None
        Song.reference_track().toggle()

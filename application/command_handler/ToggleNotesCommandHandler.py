from protocol0.application.command.ToggleNotesCommand import ToggleNotesCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ToggleNotesCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ToggleNotesCommand) -> None
        Song.selected_clip().toggle_notes()

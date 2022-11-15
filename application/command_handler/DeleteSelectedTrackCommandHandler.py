from protocol0.application.command.DeleteSelectedTrackCommand import DeleteSelectedTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class DeleteSelectedTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (DeleteSelectedTrackCommand) -> None
        SongFacade.selected_track().delete()

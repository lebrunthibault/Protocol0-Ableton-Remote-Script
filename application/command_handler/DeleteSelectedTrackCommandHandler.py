from protocol0.application.command.DeleteSelectedTrackCommand import DeleteSelectedTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade


class DeleteSelectedTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (DeleteSelectedTrackCommand) -> None
        if command.track_name is not None and command.track_name != SongFacade.selected_track().name:
            raise Protocol0Warning("Cannot delete non selected '%s' track" % command.track_name)
        SongFacade.selected_track().delete()

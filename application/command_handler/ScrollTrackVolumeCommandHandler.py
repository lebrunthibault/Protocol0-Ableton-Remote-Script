from protocol0.application.command.ScrollTrackVolumeCommand import ScrollTrackVolumeCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ScrollTrackVolumeCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollTrackVolumeCommand) -> None
        SongFacade.current_track().scroll_volume(command.go_next)

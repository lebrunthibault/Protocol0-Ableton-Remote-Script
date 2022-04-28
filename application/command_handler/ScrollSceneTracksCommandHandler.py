from protocol0.application.command.ScrollSceneTracksCommand import ScrollSceneTracksCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ScrollSceneTracksCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollSceneTracksCommand) -> None
        SongFacade.selected_scene().scroll_tracks(command.go_next)

from protocol0.application.command.ScrollSceneTracksCommand import ScrollSceneTracksCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ScrollSceneTracksCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollSceneTracksCommand) -> None
        Song.selected_scene().scroll_tracks(command.go_next)

from protocol0.application.command.UnfoldSelectedSceneCommand import UnfoldSelectedSceneCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class UnfoldSelectedSceneCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (UnfoldSelectedSceneCommand) -> None
        Song.selected_scene().unfold()

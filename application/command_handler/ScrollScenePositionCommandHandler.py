from protocol0.application.command.ScrollScenePositionCommand import ScrollScenePositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ScrollScenePositionCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollScenePositionCommand) -> None
        position_scroller = Song.selected_scene().position_scroller

        position_scroller.use_fine_scrolling = command.use_fine_scrolling
        position_scroller.scroll(command.go_next)

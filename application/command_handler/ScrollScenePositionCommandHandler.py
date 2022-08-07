from protocol0.application.command.ScrollScenePositionCommand import ScrollScenePositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ScrollScenePositionCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollScenePositionCommand) -> None
        position_scroller = SongFacade.selected_scene().position_scroller

        position_scroller.use_fine_scrolling = command.use_fine_scrolling
        position_scroller.scroll(command.go_next)

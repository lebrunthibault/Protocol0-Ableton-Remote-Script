from protocol0.application.command.ScrollScenePositionCommand import ScrollScenePositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ScrollScenePositionCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ScrollScenePositionCommand) -> None
        SongFacade.selected_scene().position_scroller.scroll(command.go_next)

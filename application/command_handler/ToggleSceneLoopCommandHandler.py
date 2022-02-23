from protocol0.application.command.ToggleSceneLoopCommand import ToggleSceneLoopCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.SongFacade import SongFacade


class ToggleSceneLoopCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ToggleSceneLoopCommand) -> None
        SongFacade.selected_scene().toggle_loop()

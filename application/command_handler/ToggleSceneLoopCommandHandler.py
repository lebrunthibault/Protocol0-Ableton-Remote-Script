from protocol0.application.command.ToggleSceneLoopCommand import ToggleSceneLoopCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface


class ToggleSceneLoopCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (ToggleSceneLoopCommand) -> None
        self._song.looping_scene_toggler.toggle()

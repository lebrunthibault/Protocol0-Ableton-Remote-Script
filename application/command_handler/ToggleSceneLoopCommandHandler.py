from protocol0.application.command.ToggleSceneLoopCommand import ToggleSceneLoopCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent


class ToggleSceneLoopCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (ToggleSceneLoopCommand) -> None
        self._container.get(SceneComponent).looping_scene_toggler.toggle()

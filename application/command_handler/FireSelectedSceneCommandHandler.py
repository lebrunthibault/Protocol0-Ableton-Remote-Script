from protocol0.application.command.FireSelectedSceneCommand import FireSelectedSceneCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService


class FireSelectedSceneCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (FireSelectedSceneCommand) -> None
        self._container.get(ScenePlaybackService).fire_selected_scene()

from protocol0.application.command.FireSelectedSceneCommand import FireSelectedSceneCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService
from protocol0.shared.SongFacade import SongFacade


class FireSelectedSceneCommandHandler(CommandHandlerInterface):
    def handle(self, _):
        # type: (FireSelectedSceneCommand) -> None
        self._container.get(ScenePlaybackService).fire_scene(SongFacade.selected_scene())

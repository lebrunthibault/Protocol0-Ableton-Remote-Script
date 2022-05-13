from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.shared.SongFacade import SongFacade


class FireSceneToPositionCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (FireSceneToPositionCommand) -> None
        fire_to_position = self._container.get(SceneService).fire_scene_to_position
        if command.bar_length is not None:
            fire_to_position(SongFacade.selected_scene(), command.bar_length)
        else:
            fire_to_position(SongFacade.last_manually_started_scene())

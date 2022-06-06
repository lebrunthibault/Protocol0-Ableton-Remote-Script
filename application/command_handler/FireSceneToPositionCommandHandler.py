from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.shared.SongFacade import SongFacade


class FireSceneToPositionCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (FireSceneToPositionCommand) -> None
        """
            command.bar_length :

            is None : we fire again the last scene
            == - 1 : we fire the last bar of the previous scene
            other number : we fire the selected scene at the selected bar position
        """
        fire_to_position = self._container.get(SceneService).fire_scene_to_position
        selected_scene = SongFacade.selected_scene()

        if command.bar_length is not None:
            if command.bar_length == -1:
                self._container.get(SceneService).fire_previous_scene_to_last_bar()
            else:
                # Launching the last bar almost always means we don't want to loop
                if command.bar_length == 8 and selected_scene == SongFacade.looping_scene():
                    self._container.get(SceneComponent).looping_scene_toggler.reset()

                fire_to_position(selected_scene, command.bar_length)
        else:
            fire_to_position(SongFacade.last_manually_started_scene())

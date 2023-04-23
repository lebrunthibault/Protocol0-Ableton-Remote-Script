from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.shared.Song import Song


class FireSceneToPositionCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (FireSceneToPositionCommand) -> None
        """
        command.bar_length :

        is None : we fire again the last scene
        == - 1 : we fire the last bar of the previous scene
        other number : we fire the selected scene at the selected bar position
        """
        fire_to_position = self._container.get(ScenePlaybackService).fire_scene_to_position
        selected_scene = Song.selected_scene()
        bar_length = command.bar_length

        if bar_length is None:
            fire_to_position(Song.last_manually_started_scene())
            return

        recent_command = CommandBus.get_recent_command(
            FireSceneToPositionCommand, 0.5, except_current=True
        )

        if recent_command is not None and recent_command.bar_length == 0:
            bar_length += 10

        if bar_length == -1:
            self._container.get(ScenePlaybackService).fire_previous_scene_to_last_bar()
        else:
            # Launching the last bar almost always means we don't want to loop
            if (
                bar_length == selected_scene.bar_length - 1
                and selected_scene == Song.looping_scene()
            ):
                self._container.get(SceneComponent).looping_scene_toggler.reset()

            fire_to_position(selected_scene, bar_length)

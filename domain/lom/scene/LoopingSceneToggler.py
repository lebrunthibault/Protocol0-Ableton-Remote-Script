from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.shared.ValueToggler import ValueToggler
from protocol0.shared.SongFacade import SongFacade


class LoopingSceneToggler(ValueToggler):
    def _get_value(self):
        # type: () -> Scene
        return SongFacade.selected_scene()

    def _value_set(self, scene):
        # type: (Scene) -> None
        if scene != SongFacade.playing_scene():
            scene.fire()

        scene.scene_name.update()

    def _value_unset(self, scene):
        # type: (Scene) -> None
        scene.scene_name.update()

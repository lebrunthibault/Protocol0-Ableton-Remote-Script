import Live

from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class SceneAppearance(object):
    def __init__(self, live_scene, scene_name):
        # type: (Live.Scene.Scene, SceneName) -> None
        self._live_scene = live_scene
        self._scene_name = scene_name

    @property
    def name(self):
        # type: () -> str
        if not self._live_scene:
            return self._scene_name._cached_name
        else:
            return self._live_scene.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._live_scene and name:
            self._scene_name.set_name(name)
            self._live_scene.name = str(name).strip()

    def refresh(self):
        # type: () -> None
        Scheduler.defer(self._scene_name.update)

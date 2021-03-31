import Live

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.SceneName import SceneName
from a_protocol_0.utils.decorators import p0_subject_slot


class Scene(AbstractObject):
    def __init__(self, scene, index, *a, **k):
        # type: (Live.Scene.Scene, int) -> None
        super(Scene, self).__init__(*a, **k)
        self.index = index
        self._scene = scene
        self.scene_name = SceneName(self)
        self._is_triggered_listener.subject = self._scene

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        if not self.is_triggered and self.scene_name.bar_count and self.index < len(self.song.scenes) - 1:
            self.parent.wait_bars(self.scene_name.bar_count, self.song.scenes[self.index + 1].fire)

    def fire(self):
        self._scene.fire()

    @property
    def color(self):
        # type: () -> int
        return self._scene.color

    @color.setter
    def color(self, color):
        self._scene.color = color

    @property
    def is_triggered(self):
        # type: () -> int
        return self._scene.is_triggered

    @property
    def name(self):
        # type: () -> int
        return self._scene.name

    @name.setter
    def name(self, name):
        self._scene.name = name

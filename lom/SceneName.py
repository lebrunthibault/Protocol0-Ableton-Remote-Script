import re

from typing import TYPE_CHECKING, Any

from protocol0.lom.AbstractObjectName import AbstractObjectName

if TYPE_CHECKING:
    from protocol0.lom.Scene import Scene


class SceneName(AbstractObjectName):
    def __init__(self, scene, *a, **k):
        # type: (Scene, Any, Any) -> None
        super(SceneName, self).__init__(scene, *a, **k)
        self.scene = scene
        self._name_listener.subject = self.scene._scene

    def _get_base_name(self):
        # type: () -> str
        match = re.match("^(?P<base_name>[^\\d*()]*)",
                         self.scene.name)
        base_name = match.group("base_name").strip() if match else ""

        return base_name

    def update(self, base_name=None):
        # type: (str) -> None
        self.base_name = base_name if base_name is not None else self.base_name
        looping = "*" if self.scene == self.song.looping_scene else ""
        length_legend = self.parent.utilsManager.get_length_legend(length=self.scene.length)

        if self.scene.has_playing_clips:
            length_legend = "%s|%s" % (self.scene.current_bar + 1, length_legend)

        if self.base_name:
            scene_name = "%s (%s)%s" % (self.base_name, length_legend, looping)
        else:
            scene_name = "%s%s" % (length_legend, looping)
        self.scene.name = scene_name

import re

from typing import TYPE_CHECKING, Any

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.AbstractObjectName import AbstractObjectName
from protocol0.utils.decorators import p0_subject_slot

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
        match = re.match("^(?P<base_name>[^()]*[^()\\s])\\s*(\\((?P<length>\\d*)\\))?(?P<looping>\\*)?.*$",
                         self.scene.name)
        base_name = match.group("base_name").strip() if match else ""
        from protocol0.lom.Scene import Scene

        if match.group("looping") and not Scene.LOOPING_SCENE:
            self.scene.looping = True
        return base_name

    @property
    def _length_legend(self):
        # type: () -> str
        if int(self.scene.length) % self.song.signature_numerator != 0:
            return "%d beat%s" % (self.scene.length, "s" if self.scene.length > 1 else "")
        else:
            return "%d" % self.scene.bar_length

    def update(self, base_name=None):
        # type: (str) -> None
        self.base_name = base_name if base_name is not None else self.base_name
        # renaming numeric named scenes
        try:
            index = int(self.base_name)
            if index != self.scene.index:
                self.base_name = str(self.scene.index)
        except ValueError:
            pass

        self.scene.name = "%s (%s)%s" % (self.base_name, self._length_legend, "*" if self.scene.looping else "")

import re

from typing import TYPE_CHECKING, Any

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.lom.Scene import Scene


class SceneName(AbstractObject):
    def __init__(self, scene, *a, **k):
        # type: (Scene, Any, Any) -> None
        super(SceneName, self).__init__(*a, **k)
        self.scene = scene
        self.base_name = ""
        self._name_listener.subject = scene._scene
        self._name_listener()

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        match = re.match("^(?P<base_name>[^()]*[^()\s])\s*(\((?P<length>\d*)\))?(?P<looping>\*)?.*$", self.scene.name)
        self.base_name = match.group("base_name").strip() if match else ""
        from protocol0.lom.Scene import Scene

        if match.group("looping") and not Scene.LOOPING_SCENE:
            self.scene.looping = True

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

        self.scene.name = "%s (%d)%s" % (self.base_name, self.scene.bar_length, "*" if self.scene.looping else "")

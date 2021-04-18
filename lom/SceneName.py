import re

from typing import TYPE_CHECKING, Any

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import p0_subject_slot, defer

if TYPE_CHECKING:
    from a_protocol_0.lom.Scene import Scene


class SceneName(AbstractObject):
    def __init__(self, scene, *a, **k):
        # type: (Scene, Any, Any) -> None
        super(SceneName, self).__init__(*a, **k)
        self.scene = scene
        self.base_name = ""
        self._name_listener.subject = scene._scene
        self._name_listener()

    @p0_subject_slot("name")
    @defer
    def _name_listener(self):
        match = re.match("^(?P<base_name>[^()]*[^()\s])\s*(\((?P<length>\d*)\))?(?P<looping>\*)?.*$", self.scene.name)
        self.base_name = match.group("base_name").strip() if match else ""
        self.update()

    def update(self, base_name=None, looping=None):
        # type: (str, bool) -> None
        self.base_name = base_name if base_name is not None else self.base_name
        # renaming numeric named scenes
        try:
            index = int(self.base_name)
            if index != self.scene.index:
                self.base_name = str(self.scene.index)
        except ValueError:
            pass

        self.scene.name = "%s (%s)%s" % (self.base_name, self.scene.bar_length, "*" if self.scene.looping else "")

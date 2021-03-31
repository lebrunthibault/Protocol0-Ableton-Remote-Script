import re

from typing import TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Scene import Scene


class SceneName(AbstractObject):
    def __init__(self, scene, *a, **k):
        # type: (Scene) -> None
        super(SceneName, self).__init__(scene, *a, **k)
        self.scene = scene
        self.base_name = ""
        self.bar_count = None
        self._name_listener.subject = scene._scene
        self._name_listener()

    def __repr__(self):
        return "SceneName of %s" % self.scene

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        match = re.match("^(?P<base_name>[^()]*)(\((?P<bar_count>\d*)\))?.*$", self.scene.name)
        self.base_name = match.group("base_name").strip() if match else ""
        self.bar_count = int(match.group("bar_count")) if match and match.group("bar_count") else None

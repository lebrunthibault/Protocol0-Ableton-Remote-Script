import re

from typing import TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import p0_subject_slot, defer

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

    @p0_subject_slot("name")
    @defer
    def _name_listener(self):
        # type: () -> None
        match = re.match("^(?P<base_name>[^()]*[^()\s])\s*(\((?P<bar_count>\d*)\))?.*$", self.scene.name)
        self.base_name = match.group("base_name").strip() if match else ""
        self.bar_count = int(match.group("bar_count")) if match and match.group("bar_count") else None
        self.update()

    def update(self, base_name=None, bar_count=None):
        # type: (str) -> None
        self.base_name = base_name if base_name is not None else self.base_name
        self.bar_count = bar_count if bar_count is not None else self.bar_count
        # renaming numeric named scenes
        try:
            index = int(self.base_name)
            if index != self.scene.index:
                self.base_name = str(self.scene.index)
        except ValueError:
            pass

        name = self.base_name

        if self.bar_count:
            name = "%s (%s)" % (name, self.bar_count)
        self.scene.name = name

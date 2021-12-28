import re

from typing import TYPE_CHECKING, Any, Optional

from protocol0.lom.AbstractObjectName import AbstractObjectName
from protocol0.utils.decorators import throttle

if TYPE_CHECKING:
    from protocol0.lom.Scene import Scene


class SceneName(AbstractObjectName):
    def __init__(self, scene, *a, **k):
        # type: (Scene, Any, Any) -> None
        super(SceneName, self).__init__(*a, **k)
        self.scene = scene
        self._name_listener.subject = self.scene._scene

    def _get_base_name(self):
        # type: () -> str
        # can happen when scenes are created
        if not isinstance(self.scene.name, basestring):
            return ""
        match = re.match("^(?P<base_name>[^\\d*()]*)",
                         self.scene.name)
        base_name = match.group("base_name").strip() if match else ""

        return base_name

    @throttle(wait_time=10)
    def update(self, base_name=None, display_bar_count=True, bar_position=None):
        # type: (str, bool, Optional[int]) -> None
        """ throttling to avoid multiple calls due to name listener """
        base_name = base_name if base_name else self._get_base_name()
        looping = "*" if self.scene == self.song.looping_scene else ""
        length_legend = self.parent.utilsManager.get_length_legend(length=self.scene.length)

        if self.scene.has_playing_clips and display_bar_count:
            length_legend = "%s|%s" % (self.scene.current_bar + 1, length_legend)
        elif bar_position is not None:
            length_legend = "%s|%s" % (bar_position + 1, length_legend)

        if base_name:
            scene_name = "%s (%s)%s" % (base_name, length_legend, looping)
        else:
            scene_name = "%s%s" % (length_legend, looping)
        self.scene.name = scene_name

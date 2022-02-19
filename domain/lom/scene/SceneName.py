import re

from typing import TYPE_CHECKING, Optional

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import get_length_legend
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


class SceneName(UseFrameworkEvents):
    def __init__(self, scene):
        # type: (Scene) -> None
        super(SceneName, self).__init__()
        self.scene = scene
        self._name_listener.subject = self.scene._scene

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        Scheduler.defer(self.update)

    def _get_base_name(self):
        # type: () -> str
        # can happen when scenes are created
        if not isinstance(self.scene.name, basestring):
            return ""   # type: ignore[unreachable]
        # catches base name with or without bar length legend
        forbidden_first_character = "(?!([\\d|-]+))"
        match = re.match("^(?P<base_name>%s[^()]*)" % forbidden_first_character,
                         self.scene.name)
        base_name = match.group("base_name").strip() if match else ""

        return base_name

    def update(self, base_name=None, display_bar_count=True, bar_position=None):
        # type: (str, bool, Optional[int]) -> None
        """ throttling to avoid multiple calls due to name listener """
        base_name = base_name if base_name else self._get_base_name()
        looping = "*" if self.scene == SongFacade.looping_scene() else ""
        length_legend = get_length_legend(beat_length=self.scene.length)

        if self.scene.has_playing_clips and display_bar_count:
            length_legend = "%s|%s" % (self.scene.current_bar + 1, length_legend)
        elif bar_position is not None:
            length_legend = "%s|%s" % (bar_position + 1, length_legend)

        if base_name:
            scene_name = "%s (%s)%s" % (base_name, length_legend, looping)
        else:
            scene_name = "%s%s" % (length_legend, looping)
        self.scene.name = scene_name

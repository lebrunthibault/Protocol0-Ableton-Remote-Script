from ableton.v2.base import listens
from ableton.v2.control_surface.components import SessionNavigationComponent
from typing import Any


class P0SessionNavigationComponent(SessionNavigationComponent):
    """Deprecated ?"""

    @listens(u'offset')
    def __on_offset_changed(self, _, scene_offset):
        # type: (Any, int) -> None
        self._update_vertical()
        self._update_horizontal()
        self.song.view.selected_scene = self.song.scenes[scene_offset]

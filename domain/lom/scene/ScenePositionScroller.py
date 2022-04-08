from math import floor

from typing import List, TYPE_CHECKING, cast

from protocol0.domain.shared.ValueScroller import ValueScroller

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


class ScenePositionScroller(ValueScroller):
    def __init__(self, scene):
        # type: (Scene) -> None
        self._scene = scene
        super(ScenePositionScroller, self).__init__(1)

    def _get_values(self):
        # type: () -> List
        return range(0, self._scene.bar_length)

    def _get_initial_value(self, go_next):
        # type: (bool) -> int
        if self._scene.has_playing_clips:
            bar_position = self._scene.playing_position.bar_position
            return int(floor(bar_position) if go_next else round(bar_position))
        else:
            return cast(int, self.current_value)

    def _value_scrolled(self, bar_position):
        # type: (int) -> None
        from protocol0.domain.lom.scene.Scene import Scene
        Scene.LAST_MANUALLY_STARTED_SCENE = self._scene
        self._scene.jump_to_bar(bar_position)
        self._scene.scene_name.update(bar_position=bar_position)

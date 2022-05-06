from math import floor

from typing import List, cast

from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ScenePositionScroller(ValueScroller):
    def __init__(self, scene_length, scene_playing_state):
        # type: (SceneLength, ScenePlayingState) -> None
        self._scene_length = scene_length
        self._scene_playing_state = scene_playing_state
        super(ScenePositionScroller, self).__init__(0)

    def set_value(self, bar_position):
        # type: (int) -> None
        self._current_value = bar_position
        self._value_scrolled()

    def _get_values(self):
        # type: () -> List
        return range(0, self._scene_length.bar_length)

    def _get_initial_value(self, go_next):
        # type: (bool) -> int
        if self._scene_playing_state.has_playing_clips:
            bar_position = self._scene_playing_state.bar_position
            return int(floor(bar_position) if go_next else round(bar_position))
        else:
            return cast(int, self.current_value)

    def _value_scrolled(self):
        # type: () -> None
        DomainEventBus.emit(ScenePositionScrolledEvent())

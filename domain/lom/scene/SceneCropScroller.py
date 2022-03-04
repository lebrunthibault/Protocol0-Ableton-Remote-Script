from typing import List, TYPE_CHECKING

from protocol0.domain.shared.ValueScroller import ValueScroller

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


class SceneCropScroller(ValueScroller):
    def __init__(self, scene):
        # type: (Scene) -> None
        self._scene = scene
        super(SceneCropScroller, self).__init__(1)

    def _get_values(self):
        # type: () -> List
        bar_lengths = []
        power = 0
        while pow(2, power) <= self._scene.bar_length / 2:
            bar_lengths += [-pow(2, power), pow(2, power)]
            power += 1
        bar_lengths = list(dict.fromkeys(bar_lengths))
        bar_lengths.sort()
        return bar_lengths

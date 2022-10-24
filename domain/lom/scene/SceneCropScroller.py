from typing import List

from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.shared.ValueScroller import ValueScroller


class SceneCropScroller(ValueScroller):
    def __init__(self, scene_length):
        # type: (SceneLength) -> None
        self._scene_length = scene_length
        super(SceneCropScroller, self).__init__(1)

    def _get_values(self):
        # type: () -> List
        bar_lengths = []
        power = 0
        while pow(2, power) < self._scene_length.bar_length:
            bar_lengths += [-pow(2, power), pow(2, power)]
            power += 1
        bar_lengths = list(dict.fromkeys(bar_lengths))
        bar_lengths.sort()
        return bar_lengths

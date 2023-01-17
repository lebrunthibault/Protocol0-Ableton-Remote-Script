import collections

from typing import Dict, Any

from protocol0.domain.shared.utils.utils import get_minutes_legend
from protocol0.shared.Song import Song


class SceneStats(object):
    def __init__(self):
        # type: () -> None
        beat_duration = float(60) / Song.tempo()

        current_scene = Song.scenes()[0]
        scenes = [current_scene]

        while current_scene.next_scene and current_scene.next_scene != current_scene:
            current_scene = current_scene.next_scene
            scenes.append(current_scene)

        self.count = len(scenes)
        self.bar_length = sum([scene.bar_length for scene in scenes])
        self.total_duration = sum([scene.length for scene in scenes]) * beat_duration

    def to_dict(self):
        # type: () -> Dict
        output = collections.OrderedDict()  # type: Dict[str, Any]
        output["count"] = self.count
        output["total duration"] = get_minutes_legend(self.total_duration)

        return output

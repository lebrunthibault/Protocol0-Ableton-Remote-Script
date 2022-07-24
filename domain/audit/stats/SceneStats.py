import collections

from typing import Dict, Any

from protocol0.shared.SongFacade import SongFacade


class SceneStats(object):
    def __init__(self):
        # type: () -> None
        beat_duration = float(60) / SongFacade.tempo()

        self.count = len(SongFacade.scenes())
        self.total_duration = sum([scene.length for scene in SongFacade.scenes()]) * beat_duration

    def to_dict(self):
        # type: () -> Dict
        output = collections.OrderedDict()  # type: Dict[str, Any]
        output["count"] = self.count
        output["total duration"] = "%.2fs" % self.total_duration

        return output

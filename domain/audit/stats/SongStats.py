import collections

from typing import Dict, List

from protocol0.domain.audit.stats.ClipStats import ClipStats
from protocol0.domain.audit.stats.DeviceStats import DevicesStats
from protocol0.domain.audit.stats.SampleStats import SampleStats
from protocol0.domain.audit.stats.SceneStats import SceneStats
from protocol0.domain.audit.stats.Stats import Stats
from protocol0.domain.audit.stats.TrackStats import TrackStats
from protocol0.shared.logging.Logger import Logger


class SongStats(object):
    def __init__(self):
        # type: () -> None
        self._stats = [
            SceneStats(),
            TrackStats(),
            ClipStats(),
            DevicesStats(),
            SampleStats(),
        ]  # type: List[Stats]

    def to_dict(self):
        # type: () -> Dict
        output = collections.OrderedDict()
        for stat in self._stats:
            title = stat.__class__.__name__.replace("Stats", "").lower()
            if not title.endswith("s"):
                title += "s"
            Logger.dev("handling %s" % title)
            output[title] = stat.to_dict()

        return output

import json

from protocol0.domain.audit.stats.SongStats import SongStats
from protocol0.shared.logging.Logger import Logger


class SongStatsService(object):
    def display_song_stats(self):
        # type: () -> None
        stats = SongStats()
        # Logger.clear()
        Logger.info(json.dumps(stats.to_dict(), indent=4))

from typing import Callable

from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.infra.scheduler.BeatTime import BeatTime
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class BeatSchedulerEvent(object):
    def __init__(self, callback, beats_song_time):
        # type: (Callable, BeatTime) -> None
        self._callback = callback
        self._beats_song_execution_time = beats_song_time

    @property
    def should_execute(self):
        # type: () -> bool
        return BeatTime.make_from_beat_time(SongFacade.current_beats_song_time()) >= self._beats_song_execution_time

    @handle_error
    def execute(self):
        # type: () -> None
        Logger.log_dev("deferring")
        Scheduler.defer(self._callback)

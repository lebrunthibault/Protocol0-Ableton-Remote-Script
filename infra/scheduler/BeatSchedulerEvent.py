from typing import Callable

from protocol0.infra.scheduler.BeatTime import BeatTime
from protocol0.shared.SongFacade import SongFacade


class BeatSchedulerEvent(object):
    def __init__(self, callback, beats_song_time):
        # type: (Callable, BeatTime) -> None
        self._callback = callback
        self._beats_song_execution_time = beats_song_time

    @property
    def should_execute(self):
        # type: () -> bool
        return (
            BeatTime.from_song_beat_time(SongFacade.current_beats_song_time())
            >= self._beats_song_execution_time
        )

    def execute(self):
        # type: () -> None
        self._callback()

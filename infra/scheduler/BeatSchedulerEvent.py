from typing import Callable

from protocol0.infra.scheduler.BeatTime import BeatTime
from protocol0.shared.Song import Song


class BeatSchedulerEvent(object):
    def __init__(self, callback, beats_song_time, execute_on_song_stop):
        # type: (Callable, BeatTime, bool) -> None
        self._callback = callback
        self._beats_song_execution_time = beats_song_time
        self._execute_on_song_stop = execute_on_song_stop

    @property
    def should_execute(self):
        # type: () -> bool
        if Song.is_playing():
            return (
                    BeatTime.from_song_beat_time(Song.current_beats_song_time())
                    >= self._beats_song_execution_time
            )
        else:
            return self._execute_on_song_stop

    def execute(self):
        # type: () -> None
        self._callback()

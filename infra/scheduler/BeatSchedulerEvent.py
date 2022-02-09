from typing import Callable

from protocol0.domain.shared.decorators import handle_error
from protocol0.infra.scheduler.BeatsSongTime import BeatsSongTime
from protocol0.shared.SongFacade import SongFacade


class BeatSchedulerEvent(object):
    def __init__(self, callback, beats_song_time):
        # type: (Callable, BeatsSongTime) -> None
        self._callback = callback
        self._beats_song_execution_time = beats_song_time

    @property
    def should_execute(self):
        # type: () -> bool
        return self._beats_song_execution_time.is_after(BeatsSongTime.make_from_beat_time(SongFacade.current_beats_song_time()))

    @handle_error
    def execute(self):
        # type: () -> None
        self._callback()

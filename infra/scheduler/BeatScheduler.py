from typing import Callable

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.BeatSchedulerInterface import BeatSchedulerInterface
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.infra.scheduler.SyncedScheduler import SyncedScheduler
from protocol0.shared.SongFacade import SongFacade


class BeatScheduler(SyncedScheduler, BeatSchedulerInterface):
    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        # deferring in the case we call wait_beats just after starting the song
        Scheduler.defer(self._check_song_is_playing)
        self.schedule_message(beats, callback)

    def _check_song_is_playing(self):
        # type: () -> None
        if not SongFacade.is_playing():
            raise Protocol0Warning("Called wait_beat but song is not playing")

    def clear_scheduler(self):
        # type: () -> None
        self._pending_action_list.clear()
        self._pending_precise_action_list.clear()

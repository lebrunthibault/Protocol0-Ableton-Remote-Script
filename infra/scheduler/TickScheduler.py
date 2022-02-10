from typing import List, Callable, Optional

import Live
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.scheduler.TickSchedulerInterface import TickSchedulerInterface
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.TickSchedulerEvent import TickSchedulerEvent


class TickScheduler(TickSchedulerInterface):
    def __init__(self, beat_scheduler, song):
        # type: (BeatScheduler, Live.Song.Song) -> None
        self._beat_scheduler = beat_scheduler
        self._song = song
        self._live_timer = None  # type: Optional[Live.Base.Timer]
        # noinspection PyArgumentList
        self._scheduled_events = []  # type: List[TickSchedulerEvent]

        self.start()

    def start(self):
        # type: () -> None
        if self._live_timer:
            # noinspection PyArgumentList
            self._live_timer.stop()

        self._live_timer = Live.Base.Timer(callback=self._on_tick, interval=1, repeat=True)
        # noinspection PyArgumentList
        self._live_timer.start()

    def _stop(self):
        # type: () -> None
        del self._scheduled_events[:]
        # noinspection PyArgumentList
        self._live_timer.stop()

    @handle_error
    def _on_tick(self):
        # type: () -> None
        try:
            # this throws on startup
            if self._song.is_playing:
                self._beat_scheduler._on_tick()
        except Exception as e:
            import logging
            logging.info("is playing error: %s" % e)
            return
        for scheduled_event in self._scheduled_events[:]:
            if scheduled_event.should_execute:
                scheduled_event.execute()
                try:
                    self._scheduled_events.remove(scheduled_event)
                except ValueError:
                    pass
            else:
                scheduled_event.decrement_timeout()

    def schedule(self, tick_count, callback):
        # type: (int, Callable) -> None
        """ timeout_duration in ms """
        assert callable(callback)
        assert tick_count > 0

        scheduled_event = TickSchedulerEvent(callback=callback, tick_count=tick_count)
        self._scheduled_events.append(scheduled_event)

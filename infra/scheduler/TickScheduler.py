from typing import List, Callable

import Live
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.scheduler.TickSchedulerInterface import TickSchedulerInterface
from protocol0.infra.scheduler.TickSchedulerEvent import TickSchedulerEvent
from protocol0.shared.logging.Logger import Logger


class TickScheduler(TickSchedulerInterface):
    def __init__(self):
        # type: () -> None
        self._scheduler = Live.Base.Timer(callback=self._on_tick, interval=1, repeat=True)
        # noinspection PyArgumentList
        self._scheduler.start()
        self._scheduled_events = []  # type: List[TickSchedulerEvent]

    def restart(self):
        # type: () -> None
        self._stop()
        # noinspection PyArgumentList
        self._scheduler.start()

    def _stop(self):
        # type: () -> None
        del self._scheduled_events[:]
        # noinspection PyArgumentList
        self._scheduler.stop()

    @handle_error
    def _on_tick(self):
        # type: () -> None
        for scheduled_event in self._scheduled_events[:]:
            if scheduled_event.should_execute:
                import logging
                logging.info("executing : %s" % scheduled_event._callback)
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

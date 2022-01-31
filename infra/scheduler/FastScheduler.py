from ClyphX_Pro import ClyphXComponentBase
from typing import List, Any, Callable

import Live
from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.infra.scheduler.SchedulerEvent import SchedulerEvent


class FastScheduler(AbstractControlSurfaceComponent):
    TICK_MS_DURATION = 17  # average 17 ms

    # noinspection PyArgumentList
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(FastScheduler, self).__init__(*a, **k)
        ClyphXComponentBase.start_scheduler()
        self._scheduler = Live.Base.Timer(callback=self._on_tick, interval=1, repeat=True)
        self._scheduler.start()
        self._scheduled_events = []  # type: List[SchedulerEvent]

    def stop(self):
        # type: () -> None
        for scheduled_event in self._scheduled_events:
            scheduled_event.cancel()
        del self._scheduled_events[:]
        # noinspection PyArgumentList
        self._scheduler.stop()

    def restart(self):
        # type: () -> None
        self.stop()
        # noinspection PyArgumentList
        self._scheduler.start()

    def _on_tick(self):
        # type: () -> None
        for scheduled_event in self._scheduled_events[:]:
            if scheduled_event.is_timeout_elapsed:
                self._execute_event(scheduled_event)
            else:
                scheduled_event.decrement_timeout()

    def _execute_event(self, scheduled_event):
        # type: (SchedulerEvent) -> None
        assert scheduled_event.is_timeout_elapsed
        scheduled_event.execute()
        try:
            self._scheduled_events.remove(scheduled_event)
        except ValueError:
            pass

    def schedule(self, tick_count, callback):
        # type: (int, Callable) -> SchedulerEvent
        """ timeout_duration in ms """
        scheduled_event = SchedulerEvent(callback=callback, tick_count=tick_count)
        self._scheduled_events.append(scheduled_event)
        if scheduled_event.is_timeout_elapsed:
            self._execute_event(scheduled_event)

        return scheduled_event

    def schedule_next(self, callback):
        # type: (Callable) -> None
        self.schedule(1, callback)

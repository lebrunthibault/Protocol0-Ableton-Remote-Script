from ClyphX_Pro import ClyphXComponentBase
from typing import List, Callable, Optional

import Live
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.infra.scheduler.SchedulerEvent import SchedulerEvent


class FastScheduler(object):
    TICK_MS_DURATION = 17  # average 17 ms
    _INSTANCE = None  # type: Optional[FastScheduler]

    # noinspection PyArgumentList
    def __init__(self):
        # type: () -> None
        if self._INSTANCE:
            raise Protocol0Error("FastScheduler singleton already instantiated")
        ClyphXComponentBase.start_scheduler()
        self._scheduler = Live.Base.Timer(callback=self._on_tick, interval=1, repeat=True)
        self._scheduler.start()
        self._scheduled_events = []  # type: List[SchedulerEvent]

    @classmethod
    def get_instance(cls):
        # type: () -> FastScheduler
        if not cls._INSTANCE:
            cls._INSTANCE = FastScheduler()

        return cls._INSTANCE

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
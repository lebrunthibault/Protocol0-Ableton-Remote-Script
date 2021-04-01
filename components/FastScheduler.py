import Live
from typing import List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.utils import get_callable_name


class SchedulerEvent(AbstractObject):
    def __init__(self, callback, tick_count, *a, **k):
        # type: (callable, int) -> None
        self._executed = False
        self._callback = callback
        self._tick_count = tick_count
        self._ticks_left = tick_count

    def __repr__(self):
        return "%s (%d / %d)" % (get_callable_name(self._callback), self._ticks_left, self._tick_count)

    @property
    def is_timeout_elapsed(self):
        # type: () -> bool
        return self._ticks_left == 0

    def decrement_timeout(self):
        assert self._ticks_left > 0
        self._ticks_left -= 1

    def execute(self):
        assert not self._executed
        self._executed = True
        self._callback()


class FastScheduler(AbstractControlSurfaceComponent):
    TICK_MS_DURATION = 17  # average 17 ms

    def __init__(self, *a, **k):
        super(FastScheduler, self).__init__(*a, **k)
        self._scheduler = Live.Base.Timer(callback=self._on_tick, interval=1, repeat=True)
        self._scheduler.start()
        self._scheduled_events = []  # type: List[SchedulerEvent]

    def stop(self):
        self._scheduled_events = []
        self._scheduler.stop()

    def restart(self):
        self.stop()
        self._scheduler.start()

    def _on_tick(self):
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
        except:
            self.parent.log_dev("scheduled_event: %s" % scheduled_event)

    def schedule(self, timeout_duration, callback):
        # type: (int, callable) -> None
        """ timeout_duration in ms """
        scheduled_event = SchedulerEvent(callback=callback, tick_count=self._ms_to_tick(timeout_duration))
        if scheduled_event.is_timeout_elapsed:
            self._execute_event(scheduled_event)
        else:
            self._scheduled_events.append(scheduled_event)

    def schedule_next(self, callback):
        # type: (callable) -> None
        self.schedule(self.TICK_MS_DURATION, callback)

    def _ms_to_tick(self, duration):
        # type: (int) -> int
        """ with small ms duration we always offset to the next tick """
        if duration == 0:
            return 0
        else:
            duration = min(self.TICK_MS_DURATION, duration)
            return duration / self.TICK_MS_DURATION

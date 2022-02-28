from typing import Callable, Optional

from protocol0.domain.shared.scheduler.BeatSchedulerInterface import BeatSchedulerInterface
from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import TickSchedulerEventInterface
from protocol0.domain.shared.scheduler.TickSchedulerInterface import TickSchedulerInterface


class Scheduler(object):
    """ Facade for scheduling calls """
    _INSTANCE = None  # type: Optional[Scheduler]

    def __init__(self, tick_scheduler, beat_scheduler):
        # type: (TickSchedulerInterface, BeatSchedulerInterface) -> None
        Scheduler._INSTANCE = self
        self._tick_scheduler = tick_scheduler
        self._beat_scheduler = beat_scheduler

    @classmethod
    def defer(cls, callback):
        # type: (Callable) -> None
        cls._INSTANCE._tick_scheduler.schedule(1, callback)

    @classmethod
    def wait_beats(cls, beats, callback):
        # type: (float, Callable) -> None
        cls._INSTANCE._beat_scheduler.wait_beats(beats, callback)

    @classmethod
    def wait(cls, tick_count, callback):
        # type: (int, Callable) -> TickSchedulerEventInterface
        """ tick_count (* 17 sms) """
        return cls._INSTANCE._tick_scheduler.schedule(tick_count, callback)

    @classmethod
    def restart(cls):
        # type: () -> None
        from protocol0.shared.sequence.Sequence import Sequence
        Sequence.restart()
        cls._INSTANCE._tick_scheduler.start()
        cls._INSTANCE._beat_scheduler.restart()

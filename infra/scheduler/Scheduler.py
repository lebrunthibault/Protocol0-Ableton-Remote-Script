import threading

from typing import Callable, Optional, Union, List

from protocol0.application.config import Config
from protocol0.domain.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.FastScheduler import FastScheduler
from protocol0.infra.scheduler.SchedulerEvent import SchedulerEvent


class Scheduler(object):
    """ Facade for scheduling calls """

    @classmethod
    def defer(cls, callback):
        # type: (Callable) -> None
        FastScheduler.get_instance().schedule_next(callback)

    @classmethod
    def wait_bars(cls, bar_length, callback):
        # type: (int, Callable) -> None
        BeatScheduler.get_instance().wait_bars(bar_length, callback)

    @classmethod
    def wait_beats(cls, beats, callback):
        # type: (float, Callable) -> None
        BeatScheduler.get_instance().wait_beats(beats, callback)

    @classmethod
    def wait(cls, tick_count, callback):
        # type: (Union[int, List[int]], Callable) -> Optional[SchedulerEvent]
        """ tick_count (relative to fastScheduler) """
        assert callable(callback)

        if isinstance(tick_count, List):
            for tc in tick_count:
                cls.wait(tc, callback)
            return None

        if tick_count == 0:
            callback()
            return None
        else:
            if not Config.ABLETON_SESSION_TYPE == AbletonSessionTypeEnum.TEST:
                return FastScheduler.get_instance().schedule(tick_count=tick_count, callback=callback)
            else:
                # emulate scheduler
                threading.Timer(
                    float(tick_count) * FastScheduler.get_instance().TICK_MS_DURATION / 1000,
                    callback,
                ).start()
                return None

    @classmethod
    def clear(cls):
        # type: () -> None
        BeatScheduler.get_instance().clear_scheduler()

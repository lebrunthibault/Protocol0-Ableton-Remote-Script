from typing import Callable, Optional, Union, List

from protocol0.infra.scheduler.SchedulerEvent import SchedulerEvent


class Scheduler(object):
    """ Facade for scheduling calls """

    @classmethod
    def defer(cls, callback):
        # type: (Callable) -> None
        from protocol0.infra.scheduler.FastScheduler import FastScheduler

        FastScheduler.get_instance().schedule(1, callback)

    @classmethod
    def wait_bars(cls, bar_length, callback):
        # type: (int, Callable) -> None
        from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
        from protocol0.domain.lom.song.Song import Song

        BeatScheduler.get_instance().wait_beats(Song.get_instance().signature_numerator * bar_length, callback)

    @classmethod
    def wait_beats(cls, beats, callback):
        # type: (float, Callable) -> None
        from protocol0.infra.scheduler.BeatScheduler import BeatScheduler

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
            from protocol0.infra.scheduler.FastScheduler import FastScheduler

            return FastScheduler.get_instance().schedule(tick_count=tick_count, callback=callback)

    @classmethod
    def clear(cls):
        # type: () -> None
        from protocol0.infra.scheduler.BeatScheduler import BeatScheduler

        BeatScheduler.get_instance().clear_scheduler()

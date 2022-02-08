from typing import Callable, Optional, Union, List, TYPE_CHECKING

from protocol0.domain.shared.scheduler.BeatSchedulerInterface import BeatSchedulerInterface
from protocol0.domain.shared.scheduler.FastSchedulerInterface import FastSchedulerInterface
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.shared.scheduler.SchedulerEvent import SchedulerEvent


class Scheduler(object):
    """ Facade for scheduling calls """
    _INSTANCE = None  # type: Optional[Scheduler]

    def __init__(self, fast_scheduler, beat_scheduler):
        # type: (FastSchedulerInterface, BeatSchedulerInterface) -> None
        Scheduler._INSTANCE = self
        self._fast_scheduler = fast_scheduler
        self._beat_scheduler = beat_scheduler

    @classmethod
    def defer(cls, callback):
        # type: (Callable) -> None
        cls._INSTANCE._fast_scheduler.schedule(1, callback)

    @classmethod
    def wait_bars(cls, bar_length, callback):
        # type: (int, Callable) -> None
        cls._INSTANCE._beat_scheduler.wait_beats(SongFacade.signature_numerator() * bar_length, callback)

    @classmethod
    def wait_beats(cls, beats, callback):
        # type: (float, Callable) -> None
        cls._INSTANCE._beat_scheduler.wait_beats(beats, callback)

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
            return cls._INSTANCE._fast_scheduler.schedule(tick_count=tick_count, callback=callback)

    @classmethod
    def clear(cls):
        # type: () -> None
        from protocol0.domain.sequence.Sequence import Sequence
        for seq in reversed(Sequence.RUNNING_SEQUENCES):
            seq.cancel()
        Sequence.RUNNING_SEQUENCES = []
        cls._INSTANCE._fast_scheduler.restart()
        cls._INSTANCE._beat_scheduler.clear_scheduler()

    @classmethod
    def stop(cls):
        # type: () -> None
        from ClyphX_Pro import ParseUtils

        ParseUtils._midi_message_registry = {}  # noqa
        cls._INSTANCE._fast_scheduler.stop()

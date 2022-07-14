from typing import Callable

from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)


class TickSchedulerInterface(object):
    def schedule(self, tick_count, callback, unique=False):
        # type: (int, Callable, bool) -> TickSchedulerEventInterface
        """timeout_duration in ms"""
        raise NotImplementedError

    def start(self):
        # type: () -> None
        raise NotImplementedError

    def stop(self):
        # type: () -> None
        raise NotImplementedError

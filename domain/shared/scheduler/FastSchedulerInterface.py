from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.shared.scheduler.SchedulerEvent import SchedulerEvent


class FastSchedulerInterface(object):
    def stop(self):
        # type: () -> None
        raise NotImplementedError

    def restart(self):
        # type: () -> None
        raise NotImplementedError

    def schedule(self, tick_count, callback):
        # type: (int, Callable) -> SchedulerEvent
        """ timeout_duration in ms """
        raise NotImplementedError

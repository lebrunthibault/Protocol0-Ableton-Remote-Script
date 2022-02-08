from typing import Callable


class TickSchedulerInterface(object):
    def schedule(self, tick_count, callback):
        # type: (int, Callable) -> None
        """ timeout_duration in ms """
        raise NotImplementedError

    def restart(self):
        # type: () -> None
        raise NotImplementedError

from typing import Callable


class BeatSchedulerInterface(object):
    def wait_beats(self, beats, callback):
        # type: (float, Callable) -> None
        raise NotImplementedError

    def restart(self):
        # type: () -> None
        raise NotImplementedError

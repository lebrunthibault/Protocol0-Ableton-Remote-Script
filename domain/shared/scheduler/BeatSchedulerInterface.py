from typing import Callable


class BeatSchedulerInterface(object):
    def wait_beats(self, beats, callback, execute_on_song_stop):
        # type: (float, Callable, bool) -> None
        raise NotImplementedError

    def reset(self):
        # type: () -> None
        raise NotImplementedError

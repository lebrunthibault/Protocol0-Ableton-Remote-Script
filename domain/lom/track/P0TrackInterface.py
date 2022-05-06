import Live
from typing import Protocol


class P0TrackInterface(Protocol):
    @property
    def _track(self):
        # type: () -> Live.Track.Track
        raise NotImplementedError

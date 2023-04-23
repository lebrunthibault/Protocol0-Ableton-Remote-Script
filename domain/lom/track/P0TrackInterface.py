import Live
from typing_extensions import Protocol


class P0TrackInterface(Protocol):
    @property
    def _track(self):
        # type: () -> Live.Track.Track
        raise NotImplementedError

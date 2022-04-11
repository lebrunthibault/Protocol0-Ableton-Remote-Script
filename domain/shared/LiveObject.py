from typing import Protocol


class LiveObject(Protocol):
    @property
    def _live_ptr(self):
        # type: () -> int
        raise NotImplementedError

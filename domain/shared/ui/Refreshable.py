from typing import Protocol


class Refreshable(Protocol):
    def refresh(self):
        # type: () -> None
        raise NotImplementedError

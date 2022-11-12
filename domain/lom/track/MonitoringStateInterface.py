from typing import Protocol


class MonitoringStateInterface(Protocol):
    def switch(self):
        # type: () -> None
        raise NotImplementedError

from typing import Dict, Protocol


class Stats(Protocol):
    def to_dict(self):
        # type: () -> Dict
        raise NotImplementedError

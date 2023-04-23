from typing_extensions import Protocol
from typing import Dict


class Stats(Protocol):
    def to_dict(self):
        # type: () -> Dict
        raise NotImplementedError

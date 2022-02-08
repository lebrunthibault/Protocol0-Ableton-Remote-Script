from p0_system_client import P0SystemClient
from typing import Optional, Callable


class System(object):
    """ system facade """

    _INSTANCE = None  # type: Optional[System]

    def __init__(self, send_midi):
        # type: (Callable) -> None
        System._INSTANCE = self
        self._client = P0SystemClient(send_midi)

    @classmethod
    def client(cls):
        # type: () -> P0SystemClient
        return cls._INSTANCE._client

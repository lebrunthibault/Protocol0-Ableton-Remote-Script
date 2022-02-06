from p0_system_client import P0SystemClient
from typing import Optional


class System(object):
    """ system singleton facade """

    _INSTANCE = None  # type: Optional[P0SystemClient]

    @classmethod
    def get_instance(cls):
        # type: () -> P0SystemClient
        if not cls._INSTANCE:
            cls._INSTANCE = P0SystemClient()

        return cls._INSTANCE

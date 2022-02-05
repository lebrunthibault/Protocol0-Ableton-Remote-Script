from p0_system_api import P0SystemAPI
from typing import Optional


class System(object):
    """ system singleton facade """

    _INSTANCE = None  # type: Optional[P0SystemAPI]

    @classmethod
    def get_instance(cls):
        # type: () -> P0SystemAPI
        if not cls._INSTANCE:
            cls._INSTANCE = P0SystemAPI()

        return cls._INSTANCE

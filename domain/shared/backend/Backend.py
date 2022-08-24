from functools import wraps

from p0_backend_client import P0BackendClient
from typing import Optional, Callable, Any

from protocol0.shared.logging.Logger import Logger
from protocol0.shared.types import Func


def show_and_log(backend_client_func, log_func):
    # type: (Func, Func) -> Func
    @wraps(backend_client_func)
    def decorate(message, *a, **k):
        # type: (str, Any, Any) -> None
        log_func(message)
        backend_client_func(message, *a, **k)

    return decorate


class Backend(object):
    """Backend API facade"""

    _INSTANCE = None  # type: Optional[Backend]

    def __init__(self, send_midi):
        # type: (Callable) -> None
        Backend._INSTANCE = self
        self._client = P0BackendClient(send_midi)

        # wrap backend notification to also log
        self._client.show_info = show_and_log(self._client.show_info, Logger.info)
        self._client.show_success = show_and_log(self._client.show_success, Logger.info)
        self._client.show_warning = show_and_log(self._client.show_warning, Logger.warning)
        self._client.show_error = show_and_log(self._client.show_error, Logger.warning)

    @classmethod
    def client(cls):
        # type: () -> P0BackendClient
        return cls._INSTANCE._client

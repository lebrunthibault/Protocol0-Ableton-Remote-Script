from typing import Any, Optional

from protocol0.shared.logging.LogLevelEnum import LogLevelEnum
from protocol0.shared.logging.LoggerServiceInterface import LoggerServiceInterface


class Logger(object):
    """ Facade for logging """
    _INSTANCE = None  # type: Optional[Logger]

    def __init__(self, logger_service):
        # type: (LoggerServiceInterface) -> None
        Logger._INSTANCE = self
        self._logger = logger_service

    @classmethod
    def log_dev(cls, *a, **k):
        # type: (Any, Any) -> None
        cls._log(level=LogLevelEnum.DEV, *a, **k)

    @classmethod
    def log_debug(cls, *a, **k):
        # type: (Any, Any) -> None
        cls._log(level=LogLevelEnum.DEBUG, *a, **k)

    @classmethod
    def log_info(cls, *a, **k):
        # type: (Any, Any) -> None
        cls._log(level=LogLevelEnum.INFO, *a, **k)

    @classmethod
    def log_warning(cls, *a, **k):
        # type: (Any, Any) -> None
        cls._log(level=LogLevelEnum.WARNING, *a, **k)

    @classmethod
    def log_error(cls, message="", debug=True):
        # type: (str, bool) -> None
        cls._log(message, level=LogLevelEnum.ERROR, debug=debug)

        from protocol0.domain.shared.System import System
        System.client().show_error(message)
        if "\n" not in message:
            from protocol0.shared.logging.StatusBar import StatusBar

            StatusBar.show_message(message)

    @classmethod
    def _log(cls, message="", level=LogLevelEnum.INFO, debug=False):
        # type: (Any, LogLevelEnum, bool) -> None
        cls._INSTANCE._logger.log(
            message=message,
            debug=message is not None and debug,
            level=level,
        )

    @classmethod
    def clear(cls):
        # type: () -> None
        return None
        cls.log_info("clear_logs")

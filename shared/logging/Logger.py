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
    def log_dev(cls, message):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.DEV)

    @classmethod
    def log_debug(cls, message):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.DEBUG)

    @classmethod
    def log_info(cls, message=""):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.INFO)

    @classmethod
    def log_warning(cls, message):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.WARNING)

    @classmethod
    def log_error(cls, message="", debug=True):
        # type: (str, bool) -> None
        cls._log(message, level=LogLevelEnum.ERROR, debug=debug)

        from protocol0.domain.shared.backend.System import System
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
        cls.log_info("clear_logs")

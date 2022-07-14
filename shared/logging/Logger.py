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
    def dev(cls, message):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.DEV, debug=True)

    @classmethod
    def debug(cls, message):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.DEBUG)

    @classmethod
    def info(cls, message=""):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.INFO)

    @classmethod
    def warning(cls, message):
        # type: (Any) -> None
        cls._log(message, LogLevelEnum.WARNING)

    @classmethod
    def error(cls, message="", debug=True, show_notification=True):
        # type: (str, bool, bool) -> None
        cls._log(message, level=LogLevelEnum.ERROR, debug=debug)

        if not show_notification:
            return None

        from protocol0.domain.shared.backend.Backend import Backend
        Backend.client().show_error(message)
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
        cls.info("clear_logs")

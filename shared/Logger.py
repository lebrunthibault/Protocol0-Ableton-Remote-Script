from typing import Any, Callable, Optional

from protocol0.domain.enums.LogLevelEnum import LogLevelEnum


class Logger(object):
    """ Facade for logging """
    _INSTANCE = None  # type: Optional[Logger]

    def __init__(self, ableton_logger):
        # type: (Callable) -> None
        Logger._INSTANCE = self
        self._ableton_logger = ableton_logger

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
            from protocol0.shared.StatusBar import StatusBar

            StatusBar.show_message(message)

    @classmethod
    def _log(cls, message="", level=LogLevelEnum.INFO, debug=False):
        # type: (Any, LogLevelEnum, bool) -> None
        cls._INSTANCE._ableton_logger(
            message=message,
            debug=message is not None and debug,
            level=level,
        )

    @classmethod
    def clear(cls):
        # type: () -> None
        cls.log_info("clear_logs")

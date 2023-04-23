from typing import Callable

from typing import Optional

from protocol0.shared.logging.Logger import Logger


class StatusBar(object):
    """Facade for writing to the status bar"""

    _INSTANCE = None  # type: Optional[StatusBar]

    def __init__(self, show_message):
        # type: (Callable) -> None
        StatusBar._INSTANCE = self
        self._show_message = show_message

    @classmethod
    def show_message(cls, message):
        # type: (str) -> None
        Logger.info(message)
        # noinspection PyBroadException
        try:
            cls._INSTANCE._show_message(str(message))
        except Exception:
            Logger.warning("Couldn't show message : %s" % message)

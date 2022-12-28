import sys
from functools import partial
from traceback import extract_tb
from types import TracebackType

import Live
from typing import Any
from typing import Optional, List, Type

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ReloadScriptCommand import ReloadScriptCommand
from protocol0.application.error.SentryService import SentryService
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.backend.NotificationColorEnum import NotificationColorEnum
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.errors.error_handler import handle_error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Config import Config
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ErrorService(object):
    _DEBUG = True
    _SET_EXCEPTHOOK = False
    _IGNORED_ERROR_STRINGS = ("Cannot convert MIDI clip",)

    _IGNORED_ERROR_TYPES = "Push2.push2.QmlError"

    _IGNORED_ERROR_FILENAMES = ("\\venv\\", "\\sequence\\", "\\decorators.py")

    def __init__(self, sentry_service, song):
        # type: (SentryService, Live.Song.Song) -> None
        self._sentry_service = sentry_service
        self._song = song

        if self._SET_EXCEPTHOOK:
            sys.excepthook = self._handle_uncaught_exception
        DomainEventBus.subscribe(ErrorRaisedEvent, self._on_error_raised_event)

    def _on_error_raised_event(self, event):
        # type: (ErrorRaisedEvent) -> None
        UndoFacade.end_undo_step()
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_type and exc_value and tb
        if issubclass(exc_type, Protocol0Warning) or issubclass(exc_type, AssertionError):
            error_message = str(exc_value or exc_type).strip()
            Backend.client().show_warning(error_message or "Unknown Error")
        else:
            self._handle_exception(exc_type, exc_value, tb, event.context)

    def _handle_uncaught_exception(self, exc_type, exc_value, tb):
        # type: (Type[BaseException], BaseException, TracebackType) -> None
        if any([string in str(exc_value) for string in self._IGNORED_ERROR_STRINGS]) or any(
            [string in str(exc_type) for string in self._IGNORED_ERROR_TYPES]
        ):
            pass
        Logger.error("unhandled exception caught")
        self._handle_exception(exc_type, exc_value, tb)

    @classmethod
    def log_stack_trace(cls):
        # type: () -> None
        """This will be logged and displayed nicely by the Service"""

        @handle_error
        def raise_exception():
            # type: () -> None
            raise RuntimeError("debug stack trace")

        raise_exception()

    def _handle_exception(self, exc_type, exc_value, tb, context=None):
        # type: (Type[BaseException], BaseException, TracebackType, Optional[str]) -> None
        if self._sentry_service.activated:
            self._sentry_service.sdk.capture_exception()

        entries = [fs for fs in extract_tb(tb) if self._log_file(fs[0])]
        if self._DEBUG:
            entries = extract_tb(tb)
        error_message = "  %s  \n\n" % exc_value
        error_message += "Exception: %s\n\n" % exc_type.__name__
        if context:
            error_message += str(context) + "\n"
        error_message += "at " + "".join(self._format_list(entries[-1:], print_line=False)).strip()
        error_message += "\n\n"
        error_message += "----- traceback -----\n"
        error_message += "".join(self._format_list(entries))

        Scheduler.restart()
        # noinspection PyArgumentList
        self._song.stop_playing()  # prevent more errors coming through

        self._log_error(error_message)

    def _log_file(self, name):
        # type: (str) -> bool
        if not name:
            return False
        elif not name.startswith(Config.PROJECT_ROOT):
            return False
        elif any([string in name for string in self._IGNORED_ERROR_FILENAMES]):
            return False

        return True

    def _format_list(self, extracted_list, print_line=True):
        # type: (List[Any], bool) -> List[str]
        """Format a list of traceback entry tuples for printing.

        Given a list of tuples as returned by extract_tb() or
        extract_stack(), return a list of strings ready for printing.
        Each string in the resulting list corresponds to the item with the
        same index in the argument list.  Each string ends in a newline;
        the strings may contain internal newlines as well, for those items
        whose source text line is not None.
        """
        trace_list = []

        for filename, lineno, name, line in extracted_list:  # type: (str, int, str, str)
            item = "  %s, line %d, in %s\n" % (
                filename.replace(Config.PROJECT_ROOT, "../components"),
                lineno,
                name,
            )
            if line and print_line:
                item = item + "    %s\n" % line.strip()
            trace_list.append(item)
        return trace_list

    def _log_error(self, message):
        # type: (str) -> None
        Logger.error(message, show_notification=False, debug=False)

        seq = Sequence()
        seq.prompt(
            "%s\n\nReload script ?" % message,
            vertical=False,
            color=NotificationColorEnum.ERROR,
            default=False,
        )
        seq.add(partial(CommandBus.dispatch, ReloadScriptCommand()))
        seq.done()

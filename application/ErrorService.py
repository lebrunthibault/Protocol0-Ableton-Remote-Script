import sys
from traceback import extract_tb
from types import TracebackType

from typing import Optional, Any, List, Type

from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.System import System
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Config import Config
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger


class ErrorService(object):
    _SET_EXCEPTHOOK = False
    _IGNORED_ERROR_STRINGS = (
        "Cannot convert MIDI clip",
    )

    _IGNORED_ERROR_TYPES = (
        "Push2.push2.QmlError"
    )

    _IGNORED_ERROR_FILENAMES = (
        "\\venv\\",
        "\\sequence\\"
    )

    def __init__(self):
        # type: () -> None
        if self._SET_EXCEPTHOOK:
            sys.excepthook = self._handle_uncaught_exception
        DomainEventBus.subscribe(ErrorRaisedEvent, self._handle_error_event)

    def _handle_error_event(self, event):
        # type: (ErrorRaisedEvent) -> None
        UndoFacade.end_undo_step()
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_type and exc_value and tb
        if issubclass(exc_type, Protocol0Warning):
            System.client().show_warning(str(exc_value or exc_type))
        else:
            self._handle_exception(exc_type, exc_value, tb, event.context)

    def _handle_uncaught_exception(self, exc_type, exc_value, tb):
        # type: (Type[BaseException], BaseException, TracebackType) -> None
        if any([string in str(exc_value) for string in self._IGNORED_ERROR_STRINGS]) or \
                any([string in str(exc_type) for string in self._IGNORED_ERROR_TYPES]):
            pass
        Logger.log_error("unhandled exception caught !!")
        self._handle_exception(exc_type, exc_value, tb)

    def _handle_exception(self, exc_type, exc_value, tb, context=None):
        # type: (Type[BaseException], BaseException, TracebackType, Optional[str]) -> None
        show = [fs for fs in extract_tb(tb) if self._check_file(fs[0])]
        error_message = "----- %s (%s) -----\n" % (exc_value, exc_type)
        if context:
            error_message += (str(context) + "\n")
        error_message += "at " + "".join(self._format_list(show[-1:], print_line=False)).strip()
        error_message += "\n\n"
        error_message += "----- traceback -----\n"
        error_message += "".join(self._format_list(show))

        Logger.log_error(error_message)

        Scheduler.restart()
    #
    #     Scheduler.wait(10, self._restart)
    #
    # def _restart(self):
    #     # type: () -> None
    #     Logger.log_warning("Error handled: reinitializing song")
    #     CommandBus.dispatch(InitializeSongCommand())

    def _check_file(self, name):
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
            item = "  %s, line %d, in %s\n" % (filename.replace(Config.PROJECT_ROOT, "../components"), lineno, name)
            if line and print_line:
                item = item + "    %s\n" % line.strip()
            trace_list.append(item)
        return trace_list
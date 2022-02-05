import sys
from traceback import extract_tb
from types import TracebackType

from typing import Optional, Any, List, Type

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.application.config import Config
from protocol0.application.constants import PROJECT_ROOT
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.infra.System import System


class ErrorManager(AbstractControlSurfaceComponent):
    IGNORED_ERROR_STRINGS = (
        "Cannot convert MIDI clip",
    )

    IGNORED_ERROR_TYPES = (
        "Push2.push2.QmlError"
    )

    IGNORED_ERROR_FILENAMES = (
        "\\venv\\",
        "\\sequence\\"
    )

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ErrorManager, self).__init__(*a, **k)
        self._original_excepthook = sys.excepthook
        if Config.SET_EXCEPTHOOK:
            sys.excepthook = self.handle_uncaught_exception

    def handle_error(self, context=None):
        # type: (Optional[str]) -> None
        if self.song:
            self.song.end_undo_step()
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_type and exc_value and tb
        if issubclass(exc_type, Protocol0Warning):
            System.get_instance().show_warning(str(exc_value or exc_type))
        else:
            self._handle_exception(exc_type, exc_value, tb, context)

    def handle_uncaught_exception(self, exc_type, exc_value, tb):
        # type: (Type[BaseException], BaseException, TracebackType) -> None
        if any([string in str(exc_value) for string in self.IGNORED_ERROR_STRINGS]) or \
                any([string in str(exc_type) for string in self.IGNORED_ERROR_TYPES]):
            pass
        self.parent.log_error("unhandled exception caught !!")
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

        self.parent.log_error(error_message)

        self.parent.clear_tasks()

        self.parent.wait(10, self._restart)

    def _restart(self):
        # type: () -> None
        self.parent.log_warning("Error handled: reinitializing song")
        self.parent.songManager.init_song()

    def _check_file(self, name):
        # type: (str) -> bool
        if not name:
            return False
        elif not name.startswith(PROJECT_ROOT):
            return False
        elif any([string in name for string in self.IGNORED_ERROR_FILENAMES]):
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
            item = "  %s, line %d, in %s\n" % (filename.replace(PROJECT_ROOT, "../components"), lineno, name)
            if line and print_line:
                item = item + "    %s\n" % line.strip()
            trace_list.append(item)
        return trace_list

    def disconnect(self):
        # type: () -> None
        super(ErrorManager, self).disconnect()
        if Config.SET_EXCEPTHOOK:
            sys.excepthook = self._original_excepthook

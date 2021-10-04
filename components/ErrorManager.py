import sys
from traceback import extract_tb
from types import TracebackType

from typing import Optional, Any, List, Type

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.config import PROJECT_ROOT, Config


class ErrorManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ErrorManager, self).__init__(*a, **k)
        if Config.SET_EXCEPTHOOK:
            sys.excepthook = self.handle_uncaught_exception

    def handle_error(self, context=None):
        # type: (Optional[str]) -> None
        self.song.end_undo_step()
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_type and exc_value and tb
        self._handle_exception(exc_type, exc_value, tb, context)

    def handle_uncaught_exception(self, exc_type, exc_value, tb):
        # type: (Type[BaseException], BaseException, TracebackType) -> None
        # if "Cannot convert MIDI clip" in str(exc_value):
        #     self.parent.log_warning(exc_value)
        #     return
        self.parent.log_error("unhandled exception caught !!")
        self._handle_exception(exc_type, exc_value, tb)

    def _handle_exception(self, exc_type, exc_value, tb, context=None):
        # type: (Type[BaseException], BaseException, TracebackType, Optional[str]) -> None
        show = [fs for fs in extract_tb(tb) if self._check_file(fs[0])]
        self.parent.log_error("----- %s (%s) -----" % (exc_value, exc_type), debug=False)
        if context:
            self.parent.log_error(context, debug=False)
        self.parent.log_error("at " + "".join(self._format_list(show[-1:], print_line=False)).strip(), debug=False)
        self.parent.log_error()
        self.parent.log_error("----- traceback -----", debug=False)
        self.parent.log_error("".join(self._format_list(show)), debug=False)

        self.song.errored = True
        self.parent.clear_tasks()
        self.parent.defer(self.song.reset)

        if not self.parent.test_mode:
            self.parent.wait(100, self._restart)

    def _restart(self):
        # type: () -> None
        self.song.errored = False
        self.parent.start()

    def _check_file(self, name):
        # type: (str) -> bool
        return bool(name and name.startswith(PROJECT_ROOT))

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
            item = "  %s, line %d, in %s\n" % (filename.replace(PROJECT_ROOT, "."), lineno, name)
            if line and print_line:
                item = item + "    %s\n" % line.strip()
            trace_list.append(item)
        return trace_list

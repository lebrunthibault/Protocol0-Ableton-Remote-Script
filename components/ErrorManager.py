import sys
import traceback
from traceback import extract_tb, format_exception_only

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import ROOT_DIR


class ErrorManager(AbstractControlSurfaceComponent):
    def __init__(self, set_excepthook=False, *a, **k):
        super(ErrorManager, self).__init__(*a, **k)
        if set_excepthook:
            sys.excepthook = self.handle_uncaught_exception

    def handle_error(self, e, context=None):
        # type: (Exception) -> None
        exc_type, exc_value, tb = sys.exc_info()
        self._handle_exception(exc_type, exc_value, tb, context)

    def handle_uncaught_exception(self, exc_type, exc_value, tb):
        self._handle_exception(exc_type, exc_value, tb)

    def _handle_exception(self, exc_type, exc_value, tb, context=None):
        show = [fs for fs in extract_tb(tb) if self._check_file(fs[0])]
        self.parent.log_error("----- %s -----" % exc_value, debug=False)
        if context:
            self.parent.log_error(context, debug=False)
        self.parent.log_error('at ' + ''.join(self._format_list(show[-1:], print_line=False)).strip(), debug=False)
        self.parent.log_error()
        self.parent.log_error("----- traceback -----", debug=False)
        self.parent.log_error(''.join(self._format_list(show)), debug=False)

        self.song.errored = True
        self.parent.fastScheduler.restart()
        self.parent.defer(self.song.reset)

    def _check_file(self, name):
        return name and name.startswith(ROOT_DIR)

    def _format_list(self, extracted_list, print_line=True):
        """Format a list of traceback entry tuples for printing.

        Given a list of tuples as returned by extract_tb() or
        extract_stack(), return a list of strings ready for printing.
        Each string in the resulting list corresponds to the item with the
        same index in the argument list.  Each string ends in a newline;
        the strings may contain internal newlines as well, for those items
        whose source text line is not None.
        """
        list = []

        for filename, lineno, name, line in extracted_list:  # type: (str, int, str, str)
            item = '  %s, line %d, in %s\n' % (filename.replace(ROOT_DIR, "."), lineno, name)
            if line and print_line:
                item = item + '    %s\n' % line.strip()
            list.append(item)
        return list

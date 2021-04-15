import sys
from traceback import extract_tb, format_exception_only

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import ROOT_DIR


class ErrorManager(AbstractControlSurfaceComponent):
    def handle_error(self, e):
        # type: (Exception) -> None
        exc_type, exc_value, tb = sys.exc_info()
        show = (fs for fs in extract_tb(tb) if self._check_file(fs[0]))
        fmt = self._format_list(show) + format_exception_only(e.__class__.__name__, e)
        self.parent.log_error()
        self.parent.log_error("----- %s -----" % e, debug=False)
        self.parent.log_error()
        self.parent.log_error(''.join(fmt), debug=False)

    def _check_file(self, name):
        return name and name.startswith(ROOT_DIR)

    def _format_list(self, extracted_list):
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
            if line:
                item = item + '    %s\n' % line.strip()
            list.append(item)
        return list

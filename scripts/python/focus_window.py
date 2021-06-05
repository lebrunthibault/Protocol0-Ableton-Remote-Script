import sys

import win32gui
from typing import Optional
from utils import setup_logs, log

from a_protocol_0.enums.AbstractEnum import AbstractEnum

window_name = sys.argv[1]


class SearchType(AbstractEnum):
    NAME = "NAME"
    EXE = "EXE"


def focus_window(name, search_type):
    # type: (str, Optional[str]) -> None
    search_type = SearchType.get_from_value(search_type, SearchType.NAME)

    if search_type == SearchType.NAME:
        find_func = partial
        args = (None, name)
    else:
        win32gui.SetForegroundWindow(win32gui.FindWindowEx(None, name))
        return
        args = (name, None)

    try:
        win32gui.SetForegroundWindow(win32gui.FindWindow(*args))
        log("Window focused : %s" % window_name)
    except Exception as e:
        log("Error on %s: %s" % (window_name, e))


if __name__ == "__main__":
    setup_logs()
    try:
        search_type = sys.argv[2]
    except IndexError:
        search_type = None

    focus_window(sys.argv[1], search_type)

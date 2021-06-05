from functools import partial

import win32gui
import win32process
import wmi
from typing import Optional, Any
from utils.log import log

from a_protocol_0.consts import ABLETON_EXE
from a_protocol_0.enums.AbstractEnum import AbstractEnum

c = wmi.WMI()
SEARCH_WINDOW_HANDLE = {"hwnd": 0}


def _get_app_path(hwnd):
    # type: (int) -> Optional[str]
    """Get application path given hwnd."""
    # noinspection PyBroadException
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        for p in c.query("SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            exe = p.ExecutablePath
            break
    except Exception:
        return None
    else:
        return exe


def _get_app_name(hwnd):
    # type: (int) -> Optional[str]
    """Get application filename given hwnd."""
    # noinspection PyBroadException
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        for p in c.query("SELECT Name FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            exe = p.Name
            break
    except Exception:
        return None
    else:
        return exe


def find_search_window_handle(class_name=None, app_name=None):
    # type: (Optional[str], Optional[str]) -> Optional[int]
    assert class_name or app_name, "You should give a criteria to search a window"

    def winEnumHandler(hwnd, _):
        # type: (int, Any) -> None
        if (
            win32gui.IsWindowVisible(hwnd)
            and (not class_name or win32gui.GetClassName(hwnd) == class_name)
            and (not app_name or _get_app_name(hwnd) == app_name)
        ):
            SEARCH_WINDOW_HANDLE["hwnd"] = hwnd

    win32gui.EnumWindows(winEnumHandler, None)

    return SEARCH_WINDOW_HANDLE["hwnd"]


class SearchType(AbstractEnum):
    NAME = "NAME"
    EXE = "EXE"


def focus_window(name, search_type):
    # type: (str, SearchType) -> None
    if search_type == SearchType.NAME:
        find_func = partial(win32gui.FindWindowEx, None, name)
    else:
        find_func = partial(find_search_window_handle, app_name=name)

    try:
        window = find_func()
        log("Window found : %s" % window)
    except Exception as e:
        log("Error on %s: %s" % (name, e))

    win32gui.SetForegroundWindow(window)
    log("Window focused : %s" % window)


def focus_ableton():
    # type: () -> None
    focus_window(ABLETON_EXE, SearchType.EXE)

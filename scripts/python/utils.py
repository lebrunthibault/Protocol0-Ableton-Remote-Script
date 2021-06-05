import os
import subprocess
import sys
from datetime import datetime

import win32api
import win32con
import win32gui
import win32process
import wmi

# noinspection PyUnresolvedReferences
from PIL import ImageGrab
from search_set import create_gui
from typing import Optional
from typing import Tuple
from utils import log

from a_protocol_0.consts import SERVER_DIR

c = wmi.WMI()

SEARCH_WINDOW_HANDLE = {"hwnd": None}

from a_protocol_0.enums.ColorEnum import InterfaceColorEnum

LOG_DIRECTORY = "C:\\Users\\thiba\\OneDrive\\Documents\\protocol0_logs"


def click_and_restore_pos(x, y):
    # type: (int, int) -> None
    (orig_x, orig_y) = win32api.GetCursorPos()
    _click(x, y)
    win32api.SetCursorPos((orig_x, orig_y))


def _click(x, y):
    # type: (int, int) -> None
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def get_pixel_color(x, y):
    # type: (int, int) -> Tuple[int, int, int]
    image = ImageGrab.grab()
    pixel_color = image.getpixel((x, y))
    log("pixel_color: %s" % InterfaceColorEnum.get_string_from_tuple(pixel_color))
    return pixel_color


def _get_log_filename():
    # type: () -> str
    return os.path.join(LOG_DIRECTORY, os.path.basename(sys.argv[0])).replace(".py", ".txt")


def setup_logs():
    # type: () -> None
    if os.path.exists(_get_log_filename()):
        os.remove(_get_log_filename())


def log(message):
    # type: (str) -> None
    """ expecting sequential script execution """
    message = "%s : %s\n" % (datetime.now(), message)
    print(message)
    with open(_get_log_filename(), "a") as f:
        f.write(message)


def get_app_path(hwnd):
    # type: (int) -> Optional[str]
    """Get application path given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query("SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            exe = p.ExecutablePath
            break
    except:
        return None
    else:
        return exe


def get_app_name(hwnd):
    # type: (int) -> Optional[str]
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query("SELECT Name FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            exe = p.Name
            break
    except:
        return None
    else:
        return exe


def find_search_window_handle(class_name=None, app_name=None):
    # type: (Optional[str], Optional[str]) -> None
    def winEnumHandler(hwnd, _):
        if (
            win32gui.IsWindowVisible(hwnd)
            and (not class_name or win32gui.GetClassName(hwnd) == class_name)
            and (not app_name or get_app_name(hwnd) == app_name)
        ):
            SEARCH_WINDOW_HANDLE["hwnd"] = hwnd

    win32gui.EnumWindows(winEnumHandler, None)

    if SEARCH_WINDOW_HANDLE["hwnd"]:
        log("found search set window, focusing")
        win32gui.SetForegroundWindow(SEARCH_WINDOW_HANDLE["hwnd"])
    else:
        log("didn't find search set window, creating gui")
        create_gui()
        subprocess.Popen([SERVER_DIR + "\\gui\\protocol0_search.bat"], shell=True)
        # KeyBoardShortcutManager.execute_batch(SERVER_DIR + "\\gui\\protocol0_search.bat")

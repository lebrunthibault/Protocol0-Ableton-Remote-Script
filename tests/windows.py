import win32gui
from typing import List, Tuple


def window_enum_handler(hwnd, resultList):
    # type: (int, List[Tuple[int, str]]) -> None
    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
        resultList.append((hwnd, win32gui.GetWindowText(hwnd)))


def get_app_list():
    # type: () -> List[Tuple[int, str]]
    handles = []  # type: List[Tuple[int, str]]
    win32gui.EnumWindows(window_enum_handler, handles)
    return handles


def focus_pycharm():
    # type: () -> None
    for app in get_app_list():
        if "Midi Remote Scripts" in app[1]:
            win32gui.SetForegroundWindow(app[0])

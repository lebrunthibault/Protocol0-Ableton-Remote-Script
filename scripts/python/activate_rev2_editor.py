import win32gui
from typing import Tuple

from send_click import click_and_restore_pos
from utils import log, setup_logs


def get_window_position(handle):
    # type: (int) -> Tuple[int, int, int, int]
    rect = win32gui.GetWindowRect(handle)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    log("Location: (%d, %d)" % (x, y))
    log("Size: (%d, %d)" % (w, h))
    return (int(x), int(y), int(w), int(h))


def get_button_middle_position(handle):
    # type: (int) -> Tuple[int, int]
    (x, y, w, h) = get_window_position(handle)
    x_button = x + w / 2
    y_button = (float(h) / 1.88) + y
    return (int(x_button), int(y_button))


def activate_rev2_editor():
    # type: () -> None
    handle = win32gui.FindWindowEx(None, None, None, "REV2Editor/midi")
    log("found handle for rev2 editor: %s" % handle)
    if not handle:
        return
    (x, y) = get_button_middle_position(handle)
    win32gui.SetForegroundWindow(handle)
    click_and_restore_pos(x, y)


if __name__ == "__main__":
    setup_logs()
    activate_rev2_editor()

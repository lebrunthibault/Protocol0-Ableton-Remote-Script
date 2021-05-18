import os
import time

import win32gui
from typing import Tuple

from send_click import click_and_restore_pos

LOG_FILE = "C:\\Users\\thiba\\OneDrive\\Documents\\protocol0_logs\\log_activate_rev2_editor.txt"

if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)


def log(message):
    # type: (str) -> None
    message = "%s : %s\n" % (time.time(), message)
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message)


def get_window_position(handle):
    # type: (int) -> Tuple[int, int, int, int]
    rect = win32gui.GetWindowRect(handle)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    log("\tLocation: (%d, %d)" % (x, y))
    log("\t    Size: (%d, %d)" % (w, h))
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
    log("handle: %s" % handle)
    (x, y) = get_button_middle_position(handle)
    win32gui.SetForegroundWindow(handle)
    click_and_restore_pos(x, y)


if __name__ == "__main__":
    activate_rev2_editor()

import logging
from typing import Tuple

import win32gui
from lib.click import click_and_restore_pos
from lib.window.window import get_window_position


def get_button_middle_position(handle):
    # type: (int) -> Tuple[int, int]
    (x, y, w, h) = get_window_position(handle)
    x_button = x + w / 2
    y_button = (float(h) / 1.88) + y
    return (int(x_button), int(y_button))


def activate_rev2_editor():
    # type: () -> None
    handle = win32gui.FindWindowEx(None, None, None, "REV2Editor/midi")
    logging.info("found handle for rev2 editor: %s" % handle)
    if not handle:
        return
    (x, y) = get_button_middle_position(handle)
    win32gui.SetForegroundWindow(handle)
    click_and_restore_pos(x, y)


if __name__ == "__main__":
    activate_rev2_editor()

import win32api
import win32con

# noinspection PyUnresolvedReferences
from PIL import ImageGrab
from typing import Tuple
from utils.log import log

from a_protocol_0.enums.ColorEnum import InterfaceColorEnum


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

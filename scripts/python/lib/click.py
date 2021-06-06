import logging
from typing import Tuple

import win32api
import win32con
from PIL import ImageGrab
from a_protocol_0.enums.ColorEnum import InterfaceColorEnum


def click_and_restore_pos(x: int, y: int) -> None:
    (orig_x, orig_y) = win32api.GetCursorPos()
    logging.info("clicking at x: %s, y: %s" % (x, y))
    _click(x, y)
    win32api.SetCursorPos((orig_x, orig_y))


def _click(x: int, y: int) -> None:
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def get_pixel_color(x: int, y: int) -> Tuple[int, int, int]:
    image = ImageGrab.grab()
    pixel_color = image.getpixel((x, y))
    logging.info("pixel_color: %s" % InterfaceColorEnum.get_string_from_tuple(pixel_color))
    return pixel_color


def pixel_has_color(x: int, y: int, color: str) -> bool:
    res = InterfaceColorEnum.get_tuple_from_string(color) == get_pixel_color(x, y)
    logging.info("pixel_has_color -> x: %s, y: %s, color: %s, res: %s" % (x, y, color, res))
    return res

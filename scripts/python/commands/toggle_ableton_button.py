import logging
import math

from typing import Tuple
from lib.click import click_and_restore_pos, get_pixel_color

from a_protocol_0.enums.ColorEnum import InterfaceColorEnum


def _distance(c1, c2):
    # type: (Tuple[int, int, int], Tuple[int, int, int]) -> float
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def _get_closest_color_at_pixel(x, y):
    # type: (int, int) -> InterfaceColorEnum
    return sorted(list(InterfaceColorEnum), key=lambda c: _distance(c.get_tuple(), get_pixel_color(x, y)))[0]


def toggle_ableton_button(x: int, y: int, activate: bool) -> None:
    logging.info("x: %s, y: %s, activate: %s" % (x, y, activate))
    closest_color = _get_closest_color_at_pixel(x, y)
    logging.info("closest_color: %s" % closest_color)
    if (activate and closest_color == InterfaceColorEnum.DEACTIVATED) or (
            not activate and closest_color == InterfaceColorEnum.ACTIVATED
    ):
        logging.info("color matching expectation, dispatching click")
        click_and_restore_pos(x, y)
    else:
        logging.info("color %s not matching expectation, skipping" % closest_color)

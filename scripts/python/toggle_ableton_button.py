import math
import sys

from typing import Tuple

from a_protocol_0.enums.ColorEnum import InterfaceColorEnum
from utils import click_and_restore_pos, log, setup_logs, get_pixel_color


def distance(c1, c2):
    # type: (Tuple[int, int, int], Tuple[int, int, int]) -> float
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def get_closest_color_at_pixel(x, y):
    # type: (int, int) -> InterfaceColorEnum
    return sorted(list(InterfaceColorEnum), key=lambda c: distance(c.get_tuple(), get_pixel_color(x, y)))[0]


if __name__ == "__main__":
    setup_logs()
    x, y, activate = int(sys.argv[1]), int(sys.argv[2]), bool(int(sys.argv[3]))
    log("x: %s, y: %s, activate: %s" % (x, y, activate))
    closest_color = get_closest_color_at_pixel(x, y)
    log("closest_color: %s" % closest_color)
    if (activate and closest_color == InterfaceColorEnum.DEACTIVATED) or (
        not activate and closest_color == InterfaceColorEnum.ACTIVATED
    ):
        log("color matching expectation, dispatching click")
        click_and_restore_pos(x, y)
    else:
        log("color not matching expectation, skipping" % closest_color)

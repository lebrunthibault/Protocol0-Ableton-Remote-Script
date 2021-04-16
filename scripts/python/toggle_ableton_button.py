import math
import sys

# noinspection PyUnresolvedReferences
from PIL import ImageGrab
from typing import Tuple

from send_click import click


class Color:
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"


rgb_code_dictionary = {
    (int("ff", 16), int("A6", 16), int("08", 16)): Color.ACTIVATED,
    (int("2d", 16), int("2d", 16), int("2d", 16)): Color.DEACTIVATED,
}


def distance(c1, c2):
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def get_closest_color_at_pixel(x, y):
    # type: (Tuple) -> Color
    image = ImageGrab.grab()
    color = image.getpixel((x, y))
    colors = list(rgb_code_dictionary.keys())
    closest_colors = sorted(colors, key=lambda c: distance(c, color))
    return rgb_code_dictionary[closest_colors[0]]


if __name__ == "__main__":
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    activate = bool(int(sys.argv[3]))
    closest_color = get_closest_color_at_pixel(x, y)
    if (activate and closest_color == Color.DEACTIVATED) or (
        not activate and closest_color == Color.ACTIVATED
    ):
        click(x, y)

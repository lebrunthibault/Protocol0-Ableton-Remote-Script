from functools import partial
from math import exp


def linear(x1, y1, x2, y2, x):
    # type: (int, int, int, int, int) -> float
    """ Straight line """
    return x * ((y1 - y2) / (x1 - x2)) + ((x1 * y2) - (y1 * x2)) / (x1 - x2)


def exp_curve(x1, y1, x2, y2, x, alpha):
    # type: (int, int, int, int, int, float) -> float
    """ Exp curve like in ableton automation red alt-curves """
    f = partial(linear, x1, y1, x2, y2)

    if alpha < 0:
        y1 = y2
        x2 = x1
    return f(x) + (y1 - f(x)) * (1 - exp((x - x2) * alpha))

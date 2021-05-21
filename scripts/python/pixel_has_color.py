import sys

from a_protocol_0.enums.ColorEnum import InterfaceColorEnum
from utils import log, setup_logs, get_pixel_color


def pixel_has_color(x, y, color):
    # type: (int, int, str) -> bool
    return InterfaceColorEnum.get_tuple_from_string(color) == get_pixel_color(x, y)


if __name__ == "__main__":
    setup_logs()
    x, y, color = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    log("x: %s, y: %s, color: %s" % (x, y, color))
    if pixel_has_color(x, y, color):
        log("true")
        sys.exit(1)
    else:
        log("false")
        sys.exit(0)

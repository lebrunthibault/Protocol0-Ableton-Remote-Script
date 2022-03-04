from functools import partial

from typing import Any

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class Colorer(object):
    @classmethod
    def twinkle(cls, obj, color, secondary_color):
        # type: (Any, int, int) -> None
        if not hasattr(obj, "color"):
            raise Protocol0Warning("Cannot twinkle obj with no color : %s" % obj)

        def set_color(color):
            # type: (int) -> None
            obj.color = color

        set_color(secondary_color)
        for s in (0.5, 1.5, 2.5):
            Scheduler.wait_seconds(s, partial(set_color, color))
        for s in (1, 2):
            Scheduler.wait_seconds(s, partial(set_color, secondary_color))

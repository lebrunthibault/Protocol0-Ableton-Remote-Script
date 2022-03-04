from functools import partial

from typing import Any

from protocol0.domain.shared.ColorEnum import ColorEnum
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class Colorer(object):
    @classmethod
    def blink(cls, obj, warning_color=ColorEnum.WARNING.color_int_value):
        # type: (Any, int) -> None
        if not hasattr(obj, "color"):
            raise Protocol0Warning("Cannot twinkle obj with no color : %s" % obj)
        if hasattr(obj, "select"):
            Scheduler.defer(obj.select)

        def set_color(color):
            # type: (int) -> None
            obj.color = color

        color = obj.color

        set_color(warning_color)
        for s in (0.5, 1.5, 2.5):
            Scheduler.wait_seconds(s, partial(set_color, color))
        for s in (1, 2):
            Scheduler.wait_seconds(s, partial(set_color, warning_color))

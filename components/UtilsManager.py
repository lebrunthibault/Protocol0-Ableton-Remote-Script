import traceback

from typing import Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class UtilsManager(AbstractControlSurfaceComponent):
    def get_length_legend(self, length):
        # type: (float) -> str
        if int(length) % self.song.signature_numerator != 0:
            return "%d beat%s" % (length, "s" if length > 1 else "")
        else:
            bar_length = length / self.song.signature_numerator
            return "%d bar%s" % (bar_length, "s" if bar_length > 1 else "")

    @classmethod
    def get_legend_from_bar_length(cls, bar_length):
        # type: (int) -> str
        if bar_length == 0:
            return "unlimited bars"
        else:
            return "%d bars" % bar_length

    def print_stack(self):
        # type: () -> None
        blacklist = ["venv", "_Framework", "protocol0\\sequence", "callback_descriptor", "components\\FastScheduler"]
        for line in traceback.format_stack():
            if all([word not in line for word in blacklist]):
                self.parent.log_info(line.strip())

    @classmethod
    def compare_values(cls, value, expected_value):
        # type: (Any, Any) -> bool
        if isinstance(value, float):
            value = round(value, 3)
            expected_value = round(expected_value, 3)

        return value == expected_value

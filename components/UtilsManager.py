import traceback

from typing import Any, List

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.BarLengthEnum import BarLengthEnum


class UtilsManager(AbstractControlSurfaceComponent):
    def get_bar_length_list(self, bar_length):
        # type: (int) -> List[int]
        bar_length_list = [v.int_value for v in list(BarLengthEnum) if 0 < v.int_value <= bar_length]
        if bar_length not in bar_length_list:
            bar_length_list.append(bar_length)

        return bar_length_list

    def get_beat_time(self, bar_length=1):
        # type: (int) -> int
        """Returns the absolute beat time to use based on the given bar_length arg and current time
        signature of the song"""
        beat = int(4.0 / self.song.signature_denominator)
        return beat * self.song.signature_numerator * max(0, bar_length)

    def get_length_legend(self, length):
        # type: (float) -> str
        if int(length) % self.song.signature_numerator != 0:
            return "%d beat%s" % (length, "s" if length > 1 else "")
        else:
            bar_length = length / self.song.signature_numerator
            return "%d bar%s" % (bar_length, "s" if bar_length > 1 else "")

    @classmethod
    def get_recording_length_legend(cls, bar_length, record_tail, record_tail_bar_length):
        # type: (int, bool, int) -> str
        if bar_length == 0:
            return "Starting recording of %s" % BarLengthEnum.UNLIMITED

        bar_legend = "%d bars" % bar_length
        if record_tail:
            record_tail_legend = ""
            if record_tail_bar_length != 1:
                record_tail_legend = " %s " % BarLengthEnum.int_to_str(record_tail_bar_length)
            bar_legend = "%d bars (+%stail)" % (bar_length, record_tail_legend)
        return "Starting recording of %s" % bar_legend

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

import traceback

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class UtilsManager(AbstractControlSurfaceComponent):
    def get_beat_time(self, bar_length=1):
        # type: (int) -> int
        """Returns the absolute beat time to use based on the given bar_length arg and current time
        signature of the song"""
        beat = int(4.0 / self.song.signature_denominator)
        return beat * self.song.signature_numerator * max(0, bar_length)

    def print_stack(self):
        # type: () -> None
        blacklist = ["venv", "_Framework", "protocol0\\sequence", "callback_descriptor", "components\\FastScheduler"]
        for line in traceback.format_stack():
            if all([word not in line for word in blacklist]):
                self.parent.log_info(line.strip())

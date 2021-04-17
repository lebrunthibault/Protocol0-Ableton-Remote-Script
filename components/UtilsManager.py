from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.utils import parse_number


class UtilsManager(AbstractControlSurfaceComponent):
    def get_beat_time(self, bar_count=1):
        """Returns the absolute beat time to use based on the given bar_count arg and current time
        signature of the song"""
        beat = 4.0 / self.song._song.signature_denominator
        num = parse_number(bar_count, min_value=0, default_value=1, is_float=True)
        return beat * self.song._song.signature_numerator * num

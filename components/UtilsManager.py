from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class UtilsManager(AbstractControlSurfaceComponent):
    def get_beat_time(self, bar_count=1):
        # type: (int) -> int
        """Returns the absolute beat time to use based on the given bar_count arg and current time
        signature of the song"""
        beat = 4.0 / self.song._song.signature_denominator
        return beat * self.song._song.signature_numerator * max(0, bar_count)

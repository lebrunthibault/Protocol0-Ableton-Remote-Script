from math import floor

from protocol0.shared.SongFacade import SongFacade


class BeatsSongTime(object):
    def __init__(self, beats, sixteenths, ticks):
        # type: (int, int, int) -> None
        self.beats = beats
        self._sixteenths = sixteenths
        self._ticks = ticks  # 1 to 60

    def is_after(self, time):
        # type: (BeatsSongTime) -> bool
        return self.beats == time.beats and \
               self._sixteenths == time._sixteenths and \
               self._ticks >= time._ticks

    @classmethod
    def now(cls):
        # type: () -> BeatsSongTime
        time = SongFacade.current_beats_song_time()
        return cls(time.beats, time.sub_division, time.ticks)

    @classmethod
    def make_from_beat_count(cls, beat_count):
        # type: (float) -> BeatsSongTime
        if float(beat_count).is_integer():
            return cls(int(beat_count), 0, 0)
        else:
            beats = floor(beat_count)
            beats_reminder = (beat_count - beats)
            sixteenth_float_value = float(1) / SongFacade.signature_numerator()
            tick_float_value = float(1) / 60

            sixteenths = int(beats_reminder // sixteenth_float_value)
            sixteenths_float_reminder = beats_reminder % sixteenth_float_value
            ticks = int(sixteenths_float_reminder // tick_float_value)

            return cls(beats, sixteenths, ticks)

    @property
    def in_last_32th(self):
        # type: () -> bool
        return self.beats == SongFacade.signature_numerator() \
               and self._sixteenths == 4 \
               and self._ticks >= 30

    @property
    def in_bar_ending(self):
        # type: () -> bool
        """ Defined as during the last 64th """
        return self.in_last_32th and self._ticks >= 45

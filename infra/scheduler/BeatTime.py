from math import floor

import Live
from protocol0.shared.SongFacade import SongFacade


class BeatTime(object):
    def __init__(self, bars, beats, sixteenths, ticks):
        # type: (int, int, int, int) -> None
        self._bars = bars
        self.beats = beats
        self._sixteenths = sixteenths
        self._ticks = ticks  # 1 to 60

    def __repr__(self):
        # type: () -> str
        return "bars: %s, beats: %s, sixteenths: %s, ticks: %s" % (
            self._bars, self.beats, self._sixteenths, self._ticks)

    def __eq__(self, other):
        # type: (BeatTime) -> bool
        return self._to_tick_count == other._to_tick_count

    def __ge__(self, other):
        # type: (BeatTime) -> bool
        return self._to_tick_count >= other._to_tick_count

    @property
    def _to_tick_count(self):
        # type: () -> int
        tick_coeff = 60
        beat_coeff = 4 * tick_coeff
        bar_coeff = beat_coeff * SongFacade.signature_numerator()
        return self._ticks + self._sixteenths * 60 + self.beats * beat_coeff + self._bars * bar_coeff

    @classmethod
    def make_from_beat_time(cls, beat_time):
        # type: (Live.Song.BeatTime) -> BeatTime
        return cls(beat_time.bars, beat_time.beats, beat_time.sub_division, beat_time.ticks)

    @classmethod
    def make_from_beat_count(cls, beat_count):
        # type: (float) -> BeatTime
        if float(beat_count).is_integer():
            bars = int(beat_count / SongFacade.signature_numerator())
            beats = int(beat_count % SongFacade.signature_numerator())
            return cls(bars + 1, beats + 1, 1, 1)
        else:
            beats = floor(beat_count)
            beats_reminder = (beat_count - beats)
            bars = int(beats / SongFacade.signature_numerator())
            beats = int(beats % SongFacade.signature_numerator())
            sixteenth_float_value = float(1) / SongFacade.signature_numerator()
            tick_float_value = float(1) / 60

            sixteenths_float_reminder = beats_reminder % sixteenth_float_value

            sixteenths = int(beats_reminder // sixteenth_float_value)
            ticks = int(sixteenths_float_reminder // tick_float_value)

            return cls(bars + 1, beats + 1, sixteenths + 1, ticks + 1)

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

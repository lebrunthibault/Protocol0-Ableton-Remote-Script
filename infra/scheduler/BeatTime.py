from math import floor

import Live

from protocol0.shared.Song import Song


class BeatTime(object):
    def __init__(self, bars, beats, sixteenths, ticks):
        # type: (int, int, int, int) -> None
        self.bars = bars
        self.beats = beats
        self._sixteenths = sixteenths
        self._ticks = ticks  # 1 to 60

    def __repr__(self):
        # type: () -> str
        return "bars: %s, beats: %s, sixteenths: %s, ticks: %s" % (
            self.bars,
            self.beats,
            self._sixteenths,
            self._ticks,
        )

    def __eq__(self, other):
        # type: (object) -> bool
        return isinstance(other, BeatTime) and self._to_tick_count == other._to_tick_count

    def __ge__(self, other):
        # type: (BeatTime) -> bool
        return self._to_tick_count >= other._to_tick_count

    def __gt__(self, other):
        # type: (BeatTime) -> bool
        return self._to_tick_count > other._to_tick_count

    @property
    def _to_tick_count(self):
        # type: () -> int
        sixteenths_coeff = 60
        beat_coeff = 4 * sixteenths_coeff
        bar_coeff = beat_coeff * Song.signature_numerator()
        return (
            self._ticks
            + self._sixteenths * sixteenths_coeff
            + self.beats * beat_coeff
            + self.bars * bar_coeff
        )

    @property
    def is_start(self):
        # type: () -> bool
        return self == BeatTime(1, 1, 1, 1)

    @classmethod
    def from_song_beat_time(cls, beat_time):
        # type: (Live.Song.BeatTime) -> BeatTime
        return cls(beat_time.bars, beat_time.beats, beat_time.sub_division, beat_time.ticks)

    @classmethod
    def make_from_beat_offset(cls, beat_total_offset):
        # type: (float) -> BeatTime
        if float(beat_total_offset).is_integer():
            bars_offset = int(beat_total_offset / Song.signature_numerator())
            beats_offset = int(beat_total_offset % Song.signature_numerator())
            sixteenths_offset = 0
            ticks_offset = 0
        else:
            beats_floor_offset = floor(beat_total_offset)
            beats_reminder = beat_total_offset - beats_floor_offset
            bars_offset = int(beats_floor_offset / Song.signature_numerator())
            beats_offset = int(beats_floor_offset % Song.signature_numerator())
            sixteenth_float_value = float(1) / Song.signature_numerator()
            tick_float_value = float(1) / 60

            sixteenths_float_reminder = beats_reminder % sixteenth_float_value

            sixteenths_offset = int(beats_reminder // sixteenth_float_value)
            ticks_offset = int(sixteenths_float_reminder // tick_float_value)

        song_beat_time = Song.current_beats_song_time()

        return cls(
            bars=song_beat_time.bars + bars_offset,
            beats=song_beat_time.beats + beats_offset,
            sixteenths=song_beat_time.sub_division + sixteenths_offset,
            ticks=song_beat_time.ticks + ticks_offset,
        )

    @property
    def in_last_beat(self):
        # type: () -> bool
        return self.beats == Song.signature_numerator()

    @property
    def in_last_8th(self):
        # type: () -> bool
        return self.in_last_beat and self._sixteenths >= 3

    @property
    def in_last_16th(self):
        # type: () -> bool
        return self.in_last_beat and self._sixteenths == 4

    @property
    def in_last_32th(self):
        # type: () -> bool
        return self.in_last_16th and self._ticks >= 30

    @property
    def in_bar_ending(self):
        # type: () -> bool
        """Defined as during the last 64th"""
        return self.in_last_32th and self._ticks >= 45

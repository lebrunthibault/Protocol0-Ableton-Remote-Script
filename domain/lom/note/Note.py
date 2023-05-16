from typing import Any, Tuple

import Live

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.utils import clamp


class Note(object):
    MIN_DURATION = 1 / 128

    def __init__(self, pitch=127, start=0, duration=1, velocity=127, muted=False):
        # type: (int, float, float, int, bool) -> None
        super(Note, self).__init__()
        self._pitch = int(pitch)
        self._start = start
        self._duration = duration
        self._velocity = int(velocity)  # type: float
        self._muted = muted

    def __eq__(self, other):
        # type: (object) -> bool
        return (
            isinstance(other, Note)
            and self.pitch == other.pitch
            and self._is_value_equal(self.start, other.start)
            and self._is_value_equal(self.duration, other.duration)
            and self.muted == other.muted
        )

    def __repr__(self, **k):
        # type: (Any) -> str
        return "{start:%.2f, duration:%.2f, pitch:%s, vel:%s, muted: %s}" % (
            self.start,
            self.duration,
            self.pitch,
            self.velocity,
            self.muted,
        )

    @classmethod
    def from_midi_note(cls, note):
        # type: (Live.Clip.MidiNote) -> Note
        return Note(
            pitch=note.pitch,
            start=note.start_time,
            duration=note.duration,
            velocity=note.velocity
        )

    def to_data(self):
        # type: () -> Tuple[int, float, float, int, bool]
        return self.pitch, self.start, self.duration, int(self.velocity), self.muted

    def _is_value_equal(self, val1, val2, delta=0.00001):
        # type: (float, float, float) -> bool
        return abs(val1 - val2) < delta

    @property
    def pitch(self):
        # type: () -> int
        return int(clamp(self._pitch, 0, 127))

    @pitch.setter
    def pitch(self, pitch):
        # type: (int) -> None
        self._pitch = int(clamp(pitch, 0, 127))

    @property
    def start(self):
        # type: () -> float
        return 0 if self._start < 0 else self._start

    @start.setter
    def start(self, start):
        # type: (float) -> None
        self._start = max(float(0), start)

    @property
    def end(self):
        # type: () -> float
        return self.start + self.duration

    @end.setter
    def end(self, end):
        # type: (float) -> None
        self.duration = end - self.start

    @property
    def duration(self):
        # type: () -> float
        if self._duration <= Note.MIN_DURATION:
            return Note.MIN_DURATION
        return self._duration

    @duration.setter
    def duration(self, duration):
        # type: (int) -> None
        self._duration = max(0, duration)
        if self._duration == 0:
            raise Protocol0Error("A Note with a duration of 0 is not accepted")

    @property
    def velocity(self):
        # type: () -> float  # using float to make scaling precise
        if self._velocity < 0:
            return 0
        if self._velocity > 127:
            return 127
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        # type: (float) -> None
        self._velocity = clamp(velocity, 0, 127)

    @property
    def muted(self):
        # type: () -> bool
        return self._muted

    @muted.setter
    def muted(self, muted):
        # type: (bool) -> None
        self._muted = muted

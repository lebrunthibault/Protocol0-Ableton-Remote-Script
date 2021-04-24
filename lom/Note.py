from copy import copy
from functools import partial

from typing import TYPE_CHECKING, List, Any, cast, Optional, Tuple

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import clamp
from a_protocol_0.utils.utils import is_equal
from pushbase.note_editor_component import TimeStep

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.MidiClip import MidiClip


class Note(AbstractObject):
    MIN_DURATION = 1 / 128

    def __init__(self, pitch=127, start=0, duration=1, velocity=127, muted=False, clip=None, *a, **k):
        # type: (int, float, float, int, bool, MidiClip, Any, Any) -> None
        super(Note, self).__init__(*a, **k)
        self._pitch = int(pitch)
        self._start = start
        self._duration = duration
        self._velocity = int(velocity)
        self._muted = muted
        self.clip = cast("MidiClip", clip)

    def __eq__(self, other):
        # type: (object) -> bool
        return (
            isinstance(other, Note)
            and self.pitch == other.pitch
            and is_equal(self.start, other.start)
            and is_equal(self.duration, other.duration)
            and self.velocity == other.velocity
            and self.muted == other.muted
        )

    def __repr__(self):
        # type: () -> str
        return "{start:%.2f, duration:%.2f, pitch:%s, vel:%s, muted: %s}" % (
            self.start,
            self.duration,
            self.pitch,
            self.velocity,
            self.muted,
        )

    def to_data(self):
        # type: () -> Tuple[int, float, float, int, bool]
        return (self.pitch, self.start, self.duration, self.velocity, self.muted)

    @property
    def time_step(self):
        # type: () -> TimeStep
        """
        this is totally undocumented behavior
        but the TimeStep offset is important for removing specific notes ..
        """
        return TimeStep(self.start, self.duration)

    @property
    def pitch(self):
        # type: () -> int
        return clamp(self._pitch, 0, 127)

    @pitch.setter
    def pitch(self, pitch):
        # type: (int) -> None
        self._pitch = clamp(pitch, 0, 127)

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
        # type: () -> int
        if self._velocity < 0:
            return 0
        if self._velocity > 127:
            return 127
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        # type: (int) -> None
        self._velocity = clamp(velocity, 0, 127)

    @property
    def muted(self):
        # type: () -> bool
        return self._muted

    @muted.setter
    def muted(self, muted):
        # type: (bool) -> None
        self._muted = muted

    def overlaps(self, note):
        # type: (Note) -> bool
        return note.start < self.end and note.end > self.start

    @staticmethod
    def copy_notes(notes):
        # type: (List[Note]) -> List[Note]
        return [copy(note) for note in notes]

    @staticmethod
    def _synchronize(notes, set_notes=True):
        # type: (List[Note], bool) -> Optional[Sequence]
        for note in notes:
            [(time, length)] = note.time_step.connected_time_ranges()
            note.clip._clip.remove_notes(time, 0, length, 128)

        if set_notes:
            seq = Sequence()
            seq.add(partial(note.clip.set_notes, notes))
            return seq.done()
        else:
            return None

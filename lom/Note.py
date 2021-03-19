from copy import copy
from functools import partial

from pushbase.note_editor_component import TimeStep
from typing import TYPE_CHECKING, List

from _Framework.Util import clamp, find_if
from a_protocol_0.consts import PUSH2_BEAT_QUANTIZATION_STEPS
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import is_equal

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.MidiClip import MidiClip


class Note(AbstractObject):
    MIN_DURATION = 1 / 128
    notes_to_synchronize = set()  # type: [Note]

    def __init__(self, pitch=127, start=0, duration=1, velocity=127, muted=False, clip=None, *a, **k):
        super(Note, self).__init__(*a, **k)
        self._pitch = int(pitch)
        self._start = start
        self._duration = duration
        self._velocity = int(velocity)
        self._muted = muted
        self.clip = clip  # type: MidiClip

    def __eq__(self, other):
        return isinstance(other, Note) and \
               self.pitch == other.pitch and \
               is_equal(self.start, other.start) and \
               is_equal(self.duration, other.duration) and \
               self.velocity == other.velocity and \
               self.muted == other.muted

    def __hash__(self):
        return hash((self.pitch, self.start, self.duration, self.velocity, self.muted))

    def __repr__(self):
        return "{start:%.2f, duration:%.2f, pitch:%s, vel:%s, muted: %s}" % (
            self.start, self.duration, self.pitch, self.velocity, self.muted)

    def to_data(self):
        return (self.pitch, self.start, self.duration, self.velocity, self.muted)

    @property
    def time_step(self):
        """ this is totally undocumented behavior but the TimeStep offset is important for removing specific notes .. """
        return TimeStep(self.start, self.duration)

    @property
    def pitch(self):
        return int(clamp(self._pitch, 0, 127))

    @pitch.setter
    def pitch(self, pitch):
        self._pitch = clamp(pitch, 0, 127)

    @property
    def start(self):
        return max(0, float(self._start))

    @start.setter
    def start(self, start):
        self._start = max(0, start)

    @property
    def end(self):
        return self.start + self.duration

    @property
    def duration(self):
        if self._duration <= Note.MIN_DURATION:
            return Note.MIN_DURATION
        return float(self._duration)

    @duration.setter
    def duration(self, duration):
        self._duration = max(0, duration)
        if self._duration == 0:
            raise Protocol0Error("A Note with a duration of 0 is not accepted")

    @property
    def velocity(self):
        if self._velocity < 0:
            return 0
        if self._velocity > 127:
            return 127
        return int(self._velocity)

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = clamp(velocity, 0, 127)

    @property
    def muted(self):
        return bool(self._muted)

    @muted.setter
    def muted(self, muted):
        self._muted = bool(muted)

    def quantization(self, time):
        return find_if(lambda qtz: float(time / qtz).is_integer(), reversed(PUSH2_BEAT_QUANTIZATION_STEPS))

    @property
    def is_quantized(self):
        return self.quantization(self.start) is not None

    @property
    def is_end_quantized(self):
        return self.quantization(self.end) is not None

    def overlaps(self, note):
        # type: (Note) -> bool
        return note.start < self.end and note.end > self.start

    @staticmethod
    def copy_notes(notes):
        # type: (List[Note]) -> (List[Note])
        return [copy(note) for note in notes]

    @staticmethod
    def _synchronize(notes, set_notes=True):
        # type: (List[Note]) -> None
        for note in notes:
            [(time, length)] = note.time_step.connected_time_ranges()
            note.clip._clip.remove_notes(time, 0, length, 128)

        if set_notes:
            seq = Sequence()
            seq.add(partial(note.clip.set_notes, notes))
            return seq.done()

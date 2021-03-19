from itertools import chain

from typing import List, TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Note import Note
from a_protocol_0.automation.AutomationRampMode import AutomationRampMode
from a_protocol_0.utils.math_utils import exp_curve

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationCurveGenerator(AbstractObject):
    @classmethod
    def automation_notes(cls, clip):
        # type: (AutomationMidiClip) -> List[Note]
        return list(chain(*cls._ramp_notes(clip)))

    @classmethod
    def _ramp_notes(cls, clip):
        # type: (AutomationMidiClip) -> List[Note]
        """ ramp note endings, twice faster for notes going up as clicks happen more on notes going down  """
        notes = clip._prev_notes
        for i, next_note in enumerate(notes[1:] + [notes[0]]):
            current_note = notes[i]
            if current_note.velocity == next_note.velocity:
                yield [current_note]
            elif next_note.velocity > current_note.velocity:
                yield cls._ramp_two_notes(notes[i], next_note, clip.automation_ramp_up)
            else:
                yield cls._ramp_two_notes(notes[i], next_note, clip.automation_ramp_down)

    @classmethod
    def _ramp_two_notes(cls, start_note, end_note, ramp_mode):
        # type: (Note, Note, AutomationRampMode) -> List[Note]
        """
            2 cases : when the note is long and ramping happens at the end
            or when the note is short and the ramping takes the whole note duration
        """
        if not ramp_mode.is_active:
            yield start_note
            return

        for note in cls.generate_step_notes(start_note, end_note):
            note.velocity = exp_curve(x1=start_note.start, y1=start_note.velocity, x2=end_note.start, y2=end_note.velocity, x=note.start,
                                            alpha=ramp_mode.exp_coeff)
            yield note

    @classmethod
    def generate_step_notes(cls, start_note, end_note):
        # type: (Note, Note) -> List[Note]
        """ first note is start note. End note is end note - 1 """
        # we add one step per unit change, going as precise as possible with an integer scale
        step_count = abs(end_note.velocity - start_note.velocity)
        interval = abs(end_note.start - start_note.start) / step_count
        steps = [start_note.start + (x * interval) for x in range(0, step_count)]
        # duration is not strictly necessary here
        return [Note(start=x, duration=interval) for x in steps]

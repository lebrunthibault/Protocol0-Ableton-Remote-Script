from copy import copy
from fractions import Fraction
from functools import partial
from itertools import chain

from typing import List, TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.Note import Note
from a_protocol_0.utils.decorators import debounce
from a_protocol_0.utils.log import set_object_attr


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationMidiClip(Clip):
    def __init__(self, *a, **k):
        super(AutomationMidiClip, self).__init__(*a, **k)
        self.ramping_steps = 47
        self.ramping_duration = 0.25  # eighth note
        self._notes_listener.subject = self._clip
        self.track = self.track  # type: AutomationMidiTrack

    @subject_slot("notes")
    def _notes_listener(self):
        self._map_notes()

    @debounce(3)
    def _map_notes(self):
        notes = self.get_notes()
        if len(notes) == 0 or self._is_updating_notes or notes == self._prev_notes:
            return

        self.parent.log_debug("%s : mapping notes" % self)
        if len(self.notes_changed(notes, ["start", "duration", "pitch"])) == 0:
            self.parent.log_debug("manual pitch change")
            [setattr(note, "pitch", note.velocity) for (_, note) in self.notes_changed(notes, ["velocity"])]
            # self._notes = notes
            self.parent.defer(partial(self._map_notes, self))
            return

        if len(notes) > len(self._prev_notes) and len(self._prev_notes):
            if len(notes) - len(self._prev_notes) != 1:
                raise Exception("Multiple added notes are not handled")
            self._added_note = next(iter(list(set(notes) - set(self._prev_notes))), None)
            notes = list(set(notes) - set([self._added_note]))
            notes.sort(key=lambda x: x.start)

        note_transforms = [
            lambda notes: filter(lambda n: n.is_quantized, notes),
            self._insert_added_note,
            self._consolidate_notes,
            lambda notes: list(chain(*self._ramp_note_endings(notes))),
        ]  # type: List[callable(List[Note])]

        with set_object_attr(Note, "auto_sync_enabled", False):
            for note_transform in note_transforms:
                notes = list(note_transform(notes))
                notes.sort(key=lambda x: x.start)
            [setattr(note, "pitch", note.velocity) for note in notes]

            self.replace_all_notes(notes)
            # self.track.automated_track.automate_from_note(self.track.automated_parameter, notes)

    def _insert_added_note(self, notes):
        # type: (List[Note]) -> List[Note]
        if self._added_note is None:
            for note in notes:
                yield note
            return

        if notes[0].start != self.loop_start:
            raise Exception("the first note doesn't start on clip loop start")

        i = 0
        while i < len(notes):
            note = notes[i]
            if not self._added_note.overlaps(note):
                yield note
                i += 1
                continue

            # we check only one overlap case as the added_note cannot start before the first note

            # split 1st part of the note
            if note.start != self._added_note.start:
                truncated_note = copy(note)
                truncated_note.duration = self._added_note.start - truncated_note.start
                yield truncated_note

            while self._added_note.end >= note.end and i < len(notes) - 1:
                i += 1
                note = notes[i]
            yield self._added_note
            if self._added_note.end < note.end:
                end = note.end
                note.start = self._added_note.end
                note.duration = end - note.start
                yield note

            i += 1

    def _consolidate_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        # fill durations
        for i, next_note in enumerate(notes[1:] + [Note(start=self.length)]):
            current_note = notes[i]
            current_note.duration = next_note.start - current_note.start

        # merge notes
        current_note = notes[0]
        yield current_note
        for next_note in notes[1:]:
            if next_note.velocity == current_note.velocity:
                current_note.duration += next_note.duration
            else:
                current_note = next_note
                yield current_note

    def _ramp_note_endings(self, notes):
        # type: (List[Note]) -> List[Note]
        """ ramp note endings only for notes going down to handle the filter click on sudden changes """
        if len(notes) < 2:
            yield notes
        else:
            for i, note in enumerate(notes[1:] + [notes[0]]):
                yield self._ramp_two_notes(notes[i], note)

    def _ramp_two_notes(self, note, next_note):
        # type: (Note, Note) -> List[Note]
        """
            2 cases : when the note is long and ramping happens at the end
            or when the note is short and the ramping takes the whole note duration
        """
        if note.velocity <= next_note.velocity:
            yield note
            return

        above_ramping_duration = note.duration > self.ramping_duration * (1 + Fraction(1, self.ramping_steps))
        if above_ramping_duration:
            ramping_steps = self.ramping_steps - 1
            start_coeff = 1 - Fraction(1, self.ramping_steps)
            ramp_start = note.start + note.duration - self.ramping_duration * start_coeff
            velocity_start = note.velocity * start_coeff
            base_duration = self.ramping_duration * start_coeff

            first_note = copy(note)
            first_note.duration = note.duration - self.ramping_duration + self.ramping_duration / self.ramping_steps
            yield first_note
        else:
            ramping_steps = self.ramping_steps
            ramp_start = note.start
            velocity_start = note.velocity
            base_duration = note.duration

        for i in range(0, ramping_steps):
            coeff = float(i) / ramping_steps
            ramp_note = copy(note)
            ramp_note.start = ramp_start + (base_duration * coeff)
            ramp_note.duration = base_duration / ramping_steps
            ramp_note.velocity = round(velocity_start + (next_note.velocity - velocity_start) * coeff)
            yield ramp_note

from copy import copy
from functools import partial

from typing import List, TYPE_CHECKING, Optional, Callable, Tuple, Iterator, Union, cast

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Note import Note
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationMidiClipNoteMixin(AbstractObject):
    def _map_notes(self, notes=None, check_change=False):
        # type: (AutomationMidiClip, List[Note], bool) -> Optional[Sequence]
        notes = notes or Note.copy_notes(self._prev_notes)
        if len(notes) == 0 or (check_change and (self._is_updating_notes or notes == self._prev_notes)):
            return None

        pitch_or_vel_changes = self.notes_changed(notes, ["pitch", "velocity"])
        if len(pitch_or_vel_changes):
            self._prev_notes = notes
            return self._map_single_notes(pitch_or_vel_changes)

        if len(notes) > len(self._prev_notes) and len(self._prev_notes):
            added_notes = list(set(notes) - set(self._prev_notes))

            if len(self._prev_notes) == 0:
                notes = [added_notes[0]]
            else:
                notes = self._prev_notes
                self._added_note = added_notes[0]
                self._added_note.velocity = self._added_note.pitch

            notes.sort(key=lambda x: x.start)

        note_transforms = [
            self._filter_out_of_range_notes,
            self._filter_duplicate_notes,
            self._insert_added_note,  # handle adding a new note by splitting enclosing notes
            self._add_missing_notes,
            self._consolidate_notes,
        ]  # type: List[Callable[[List[Note]], Union[List[Note], Iterator[Note]]]]

        notes = cast(List[Note], notes)  # type: ignore[redundant-cast]  # make mypy happy
        for note_transform in note_transforms:
            notes.sort(key=lambda x: x.start)
            notes = list(set(note_transform(notes)))
            if len(notes) == 0:
                raise Protocol0Error("Problem after transform %s, no notes left" % note_transform.__name__)

        notes.sort(key=lambda x: x.start)
        for note in notes:
            note.pitch = note.velocity

        self._added_note = None

        return self.replace_all_notes(notes)

    def _map_single_notes(self, notes_change):
        # type: (AutomationMidiClip, List[Tuple[Note, Note]]) -> Sequence
        notes = [note for prev_note, note in notes_change]
        prev_notes = [prev_note for prev_note, note in notes_change]

        for prev_note, note in self.notes_changed(notes, ["pitch"], prev_notes):
            prev_note.pitch = prev_note.velocity = note.velocity = note.pitch
        for prev_note, note in self.notes_changed(notes, ["velocity"], prev_notes):
            prev_note.velocity = prev_note.pitch = note.pitch = note.velocity
        seq = Sequence()
        seq.add(partial(Note._synchronize, notes, set_notes=True))
        seq.add(self._map_notes)
        return seq.done()

    def _filter_out_of_range_notes(self, notes):
        # type: (AutomationMidiClip, List[Note]) -> List[Note]
        return list(filter(lambda n: n.start < self.loop_end and n.end > self.loop_start, notes))

    def _insert_added_note(self, notes):
        # type: (AutomationMidiClip, List[Note]) -> Iterator[Note]
        if self._added_note is None:
            for note in notes:
                yield note
            return

        notes[0].start = self.loop_start  # ensuring

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

    def _add_missing_notes(self, notes):
        # type: (AutomationMidiClip, List[Note]) -> Iterator[Note]
        # fill with min notes and check duration to stay always monophonic
        for i, next_note in enumerate(notes[1:] + [Note(start=self.loop_end)]):
            current_note = notes[i]
            if next_note.start - current_note.end > 0:
                yield current_note
                yield Note(
                    start=current_note.end,
                    duration=next_note.start - current_note.end,
                    pitch=current_note.pitch,
                    velocity=current_note.velocity,
                )
            elif next_note.start - current_note.start == 0:
                pass
            else:
                current_note.duration = next_note.start - current_note.start
                yield current_note

    def _consolidate_notes(self, notes):
        # type: (AutomationMidiClip, List[Note]) -> Iterator[Note]
        if notes[0].start != self.loop_start:
            notes = [Note(start=0, duration=notes[0].start - self.loop_start, pitch=0, velocity=0)] + notes

        notes[-1].duration = self.loop_end - notes[-1].start

        # merge same velocity notes
        current_note = notes[0]
        yield current_note
        for next_note in notes[1:]:
            if next_note.velocity == current_note.velocity:
                current_note.duration += next_note.duration
            else:
                current_note = next_note
                yield current_note

    def _filter_duplicate_notes(self, notes):
        # type: (AutomationMidiClip, List[Note]) -> List[Note]
        """
        Useful to remove bug notes at same start point
        or when a note start was stretch to the start point of another one
        """
        unique_notes_by_start_and_duration = {}

        for note in notes:
            unique_notes_by_start_and_duration["%s-%s" % (note.start, note.duration)] = note

        unique_notes = list(unique_notes_by_start_and_duration.values())
        unique_notes.sort(key=lambda x: x.start)
        return unique_notes

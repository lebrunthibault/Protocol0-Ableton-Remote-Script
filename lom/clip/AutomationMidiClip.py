from collections import defaultdict
from copy import copy
from fractions import Fraction
from functools import partial
from itertools import chain

from typing import List, TYPE_CHECKING

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.Note import Note
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import debounce, subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
    from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
    from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip


class AutomationMidiClip(Clip):
    def __init__(self, *a, **k):
        super(AutomationMidiClip, self).__init__(*a, **k)
        self.ramping_steps = 47
        self.ramping_duration = 0.25  # eighth note
        self._notes_listener.subject = self._clip
        self.track = self.track  # type: AutomationMidiTrack
        self.clip_slot = self.clip_slot  # type: AutomationMidiClipSlot
        self.automated_audio_clip = None  # type: AutomationAudioClip

    def _connect(self, clip):
        # type: (AutomationAudioClip) -> None
        if not clip:
            raise Protocol0Error("Inconsistent clip state for %s (%s)" % (self, self.track))
        self.automated_audio_clip = clip
        return clip._connect(self)

    @subject_slot("notes")
    def _notes_listener(self):
        # type: () -> Sequence
        super(AutomationMidiClip, self)._notes_listener()
        if not self._is_updating_notes:
            return self.map_notes()

    @debounce(3)
    def map_notes(self):
        notes = self.get_notes()
        if len(notes) == 0 or self._is_updating_notes or notes == self._prev_notes:
            return

        self._map_notes(notes)

    def _map_notes(self, notes=None):
        # type: (List[Note]) -> Sequence
        notes = notes or self._prev_notes

        pitch_or_vel_changes = self.notes_changed(notes, ["pitch", "velocity"])
        if len(pitch_or_vel_changes):
            return self._map_single_notes(pitch_or_vel_changes)

        base_notes = filter(lambda n: n.is_quantized, notes)
        base_prev_notes = filter(lambda n: n.is_quantized, self._prev_notes)
        if len(base_notes) > len(base_prev_notes) and len(base_prev_notes):
            added_notes_count = len(base_notes) - len(base_prev_notes)
            if added_notes_count != 1:
                raise Protocol0Error("Multiple added notes are not handled (added : %d notes on clip %s)" % (added_notes_count, self))

            self._added_note = next(iter(list(set(base_notes) - set(base_prev_notes))), None)
            notes = base_prev_notes
            self._added_note.velocity = self._added_note.pitch
            notes.sort(key=lambda x: x.start)

        note_transforms = [
            lambda notes: filter(lambda n: n.is_quantized, notes),
            self._insert_added_note,
            lambda notes: filter(lambda n: n.start < self.length, notes),
            self._consolidate_notes,
            lambda notes: list(chain(*self._ramp_note_endings(notes))),
            self._clean_duplicate_notes,
        ]  # type: List[callable(List[Note])]

        for note_transform in note_transforms:
            notes = list(note_transform(notes))
            notes = list(set(notes))
            notes.sort(key=lambda x: x.start)
            [setattr(note, "pitch", note.velocity) for note in notes]

        self._added_note = None

        return self.replace_all_notes(notes)

    def _map_single_notes(self, notes_change):
        # type: (List[Note]) -> Sequence
        notes = [note for prev_note, note in notes_change]
        prev_notes = [prev_note for prev_note, note in notes_change]

        for prev_note, note in self.notes_changed(notes, ["pitch"], prev_notes):
            prev_note.pitch = prev_note.velocity = note.velocity = note.pitch
        for prev_note, note in self.notes_changed(notes, ["velocity"], prev_notes):
            prev_note.velocity = prev_note.pitch = note.pitch = note.velocity
        seq = Sequence()
        seq.add(partial(Note._synchronize, notes))
        seq.add(self._map_notes)
        return seq.done()

    def _insert_added_note(self, notes):
        # type: (List[Note]) -> List[Note]
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

    def _consolidate_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        # fill durations
        for i, next_note in enumerate(notes[1:] + [Note(start=self.length)]):
            current_note = notes[i]
            current_note.duration = next_note.start - current_note.start

        # merge notes
        current_note = notes[0]
        current_note.duration += (current_note.start - self.loop_start)
        current_note.start = self.loop_start
        yield current_note
        for next_note in notes[1:]:
            if next_note.velocity == current_note.velocity:
                current_note.duration += next_note.duration
            else:
                current_note = next_note
                yield current_note

    def _clean_duplicate_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        notes_by_start = defaultdict(list)

        for note in notes:
            notes_by_start[note.start].append(note)
        for start, notes in notes_by_start.items():
            notes_by_start[start] = max(notes, key=lambda c: note.duration)

        notes = notes_by_start.values()
        notes.sort(key=lambda x: x.start)
        return notes

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

        is_above_ramping_duration = note.duration > self.ramping_duration * (1 + Fraction(1, self.ramping_steps))
        if is_above_ramping_duration:
            ramping_steps = self.ramping_steps - 1
            start_coeff = 1 - Fraction(1, self.ramping_steps)
            ramp_start = note.start + note.duration - self.ramping_duration * start_coeff
            velocity_start = next_note.velocity + (note.velocity - next_note.velocity) * start_coeff
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

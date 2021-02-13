from collections import defaultdict
from copy import copy
from fractions import Fraction
from functools import partial
from itertools import chain

from typing import List, TYPE_CHECKING

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import debounce, p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
    from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
    from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip


class RampModes(object):
    NO_RAMP = "NO_RAMP"
    END_RAMP = "END_RAMP"
    FULL_RAMP = "FULL_RAMP"

    @staticmethod
    def get(clip):
        # type: (AutomationMidiClip) -> str
        if "*" in clip.name:
            return RampModes.END_RAMP
        elif "+" in clip.name:
            return RampModes.FULL_RAMP
        else:
            return RampModes.NO_RAMP


class AutomationMidiClip(AbstractAutomationClip):
    RAMPING_STEPS = 47  # better be prime
    RAMPING_DURATION = 0.25  # eighth note

    def __init__(self, *a, **k):
        super(AutomationMidiClip, self).__init__(*a, **k)
        self._notes_listener.subject = self._clip
        self.track = self.track  # type: AutomationMidiTrack
        self.clip_slot = self.clip_slot  # type: AutomationMidiClipSlot
        self.automated_audio_clip = None  # type: AutomationAudioClip
        self.ramping_mode = RampModes.get(self)

    def _connect(self, clip):
        # type: (AutomationAudioClip) -> None
        if not clip:
            raise Protocol0Error("Inconsistent clip state for %s (%s)" % (self, self.track))
        self.automated_audio_clip = clip
        self._playing_status_listener.subject = self.automated_audio_clip._clip
        return clip._connect(self)

    @p0_subject_slot("notes")
    def _notes_listener(self):
        # type: () -> Sequence
        super(AutomationMidiClip, self)._notes_listener()
        if not self._is_updating_notes:
            return self.map_notes()

    @p0_subject_slot("name")
    def _name_listener(self):
        self.ramping_mode = RampModes.get(self)
        self._map_notes()

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
            # if added_notes_count != 1:
            #     raise Protocol0Error("Multiple added notes are not handled (added : %d notes on clip %s)" % (added_notes_count, self))
            if added_notes_count == 1:
                self._added_note = next(iter(list(set(base_notes) - set(base_prev_notes))), None)
                notes = base_prev_notes
                self._added_note.velocity = self._added_note.pitch
                notes.sort(key=lambda x: x.start)

        note_transforms = [
            lambda notes: filter(lambda n: n.start < self.length and n.end > self.loop_start, notes), # clean notes that outside of the clip
            self._clean_ramp_notes,  # clean not ramping
            self._insert_added_note,  # handle adding a new note by splitting enclosing notes
            self._consolidate_notes,
            lambda notes: list(chain(*self._ramp_notes(notes))),  # add note ramps if necessary
            self._clean_duplicate_notes,  # should not be necessary but sometimes multiple notes are added at the same start point
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

    def _clean_ramp_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        notes = list(filter(lambda n: n.is_quantized, notes))  # type: (List[Note])  # keep only base notes without ramping

        for i, next_note in enumerate(notes[1:] + [Note(start=self.length)]):
            if not notes[i].is_end_quantized:
                notes[i].duration = next_note.start - notes[i].start

        return notes

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
        # fill with min notes
        if notes[0].start != self.loop_start:
            notes = [Note(start=0, duration=notes[0].start - self.loop_start, pitch=0, velocity=0)] + notes

        for i, next_note in enumerate(notes[1:] + [Note(start=self.length)]):
            current_note = notes[i]
            if next_note.start - current_note.end > 0:
                # current_note.duration = next_note.start - current_note.start
                notes.append(Note(start=current_note.end, duration=next_note.start - current_note.start, pitch=0, velocity=0))

        # merge same velocity notes
        current_note = notes[0]
        yield current_note
        for next_note in notes[1:]:
            if next_note.velocity == current_note.velocity:
                current_note.duration += next_note.duration
            else:
                current_note = next_note
                yield current_note

    def _clean_duplicate_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        " Useful to remove bug notes at same start point or when a note start was stretch to the start point of another one "
        notes_by_start = defaultdict(list)

        for note in notes:
            notes_by_start[note.start].append(note)
        for start, notes in notes_by_start.items():
            notes_by_start[start] = max(notes, key=lambda note: note.duration)

        notes = notes_by_start.values()
        notes.sort(key=lambda x: x.start)
        return notes

    def _ramp_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        """ ramp note endings only for notes going down to handle the filter click on sudden changes """
        if len(notes) < 2 or self.ramping_mode == RampModes.NO_RAMP:
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

        is_above_ramping_duration = note.duration > self.RAMPING_DURATION * (1 + Fraction(1, self.RAMPING_STEPS))
        if is_above_ramping_duration and self.ramping_mode == RampModes.END_RAMP:
            ramping_steps = self.RAMPING_STEPS - 1
            start_coeff = 1 - Fraction(1, self.RAMPING_STEPS)
            ramp_start = note.start + note.duration - self.RAMPING_DURATION * start_coeff
            velocity_start = next_note.velocity + (note.velocity - next_note.velocity) * start_coeff
            base_duration = self.RAMPING_DURATION * start_coeff

            first_note = copy(note)
            first_note.duration = note.duration - self.RAMPING_DURATION + self.RAMPING_DURATION / self.RAMPING_STEPS
            yield first_note
        else:
            ramping_steps = self.RAMPING_STEPS
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

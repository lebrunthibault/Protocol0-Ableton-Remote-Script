from collections import defaultdict
from copy import copy
from functools import partial
from itertools import chain

from typing import List, TYPE_CHECKING

from a_protocol_0.enums.AutomationRampModeEnum import AutomationRampModeEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.AutomationRamp import AutomationRamp
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import debounce, p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
    from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot


class AutomationMidiClip(AbstractAutomationClip):
    RAMPING_STEPS = 47  # better be prime
    RAMPING_DURATION = 0.25  # eighth note

    def __init__(self, *a, **k):
        super(AutomationMidiClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationMidiTrack
        self.clip_slot = self.clip_slot  # type: AutomationMidiClipSlot
        self._name_listener.subject = self._clip
        self._loop_start_listener.subject = self._clip
        self._loop_end_listener.subject = self._clip
        self._notes_listener.subject = self._clip

    def _on_selected(self):
        self.view.hide_envelope()
        self.view.show_loop()

    @p0_subject_slot("loop_start")
    def _loop_start_listener(self):
        self._refresh_notes()

    @p0_subject_slot("loop_end")
    def _loop_end_listener(self):
        self._refresh_notes()

    @p0_subject_slot("notes")
    def _notes_listener(self):
        # type: () -> Sequence
        if not self._is_updating_notes:
            return self.map_notes()

    @p0_subject_slot("name")
    def _name_listener(self):
        if not self.name and self.track.linked_track:
            automated_parameter = self.track.linked_track.automated_parameter or self.parent.automationTrackManager.current_parameter
            self.clip_name.set(base_name=automated_parameter.full_name,
                               ramp_mode_up=AutomationRamp(),
                               ramp_mode_down=AutomationRamp())
        if len(self._prev_notes) >= 2:
            self._map_notes()

    def _refresh_notes(self):
        self._prev_notes = self.get_notes()
        # noinspection PyUnresolvedReferences
        self.parent.defer(self.notify_notes)

    @debounce(3)
    def map_notes(self):
        notes = self.get_notes()
        if len(notes) == 0 or self._is_updating_notes or notes == self._prev_notes:
            return

        self._map_notes(notes)

    def _map_notes(self, notes=None, check_change=False):
        # type: (List[Note]) -> Sequence
        notes = notes or Note.copy_notes(self._prev_notes)
        if len(notes) == 0 or (check_change and (self._is_updating_notes or notes == self._prev_notes)):
            return

        pitch_or_vel_changes = self.notes_changed(notes, ["pitch", "velocity"])
        if len(pitch_or_vel_changes):
            self._prev_notes = notes
            return self._map_single_notes(pitch_or_vel_changes)

        base_notes = self._filter_ramp_notes(notes)
        base_prev_notes = self._filter_ramp_notes(self._prev_notes)
        if len(base_notes) > len(base_prev_notes) and len(base_prev_notes):
            added_notes = list(set(base_notes) - set(base_prev_notes))

            if len(self._prev_notes) == 0:
                notes = [added_notes[0]]
            else:
                notes = base_prev_notes
                self._added_note = added_notes[0]
                self._added_note.velocity = self._added_note.pitch

            notes.sort(key=lambda x: x.start)

        note_transforms = [
            self._filter_out_of_range_notes,
            self._filter_duplicate_notes,
            # clean notes that outside of the clip
            self._filter_ramp_notes,  # legacy, when ramps where added to midi : clean rampings
            self._insert_added_note,  # handle adding a new note by splitting enclosing notes
            self._add_missing_notes,
            self._consolidate_notes,
        ]  # type: List[callable(List[Note])]

        for note_transform in note_transforms:
            notes.sort(key=lambda x: x.start)
            notes = list(set(note_transform(notes)))
            if len(notes) == 0:
                raise Protocol0Error("Problem after transform %s, no notes left" % note_transform.__name__)
            # self.parent.log_debug("_-__-_-_-_-_-_-_")
            # self.parent.log_debug("after transform %s" % note_transform.__name__)
            # self.parent.log_debug(notes)
            # self.parent.log_debug("_-__-_-_-_-_-_-_")

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
        seq.add(partial(Note._synchronize, notes, set_notes=True))
        seq.add(self._map_notes)
        return seq.done()

    @property
    def automation_notes(self):
        # type: () -> List[Note]
        if len(self._prev_notes) == 0:
            return []

        notes = list(chain(*self._ramp_notes(self._prev_notes)))
        # should not be necessary but sometimes multiple notes are added at the same start point
        notes = self._remove_start_short_notes(notes)
        notes.sort(key=lambda x: x.start)

        return notes

    def _filter_out_of_range_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        return filter(lambda n: n.start < self.loop_end and n.end > self.loop_start, notes)

    def _filter_ramp_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        if len(notes) == 0:
            return []

        notes = list(
            filter(lambda n: n.is_quantized, notes))  # type: (List[Note])  # keep only base notes without ramping

        for i, next_note in enumerate(notes[1:] + [Note(start=self.loop_end)]):
            if not notes[i].is_end_quantized:
                if next_note.start - notes[i].start > 0:
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

    def _add_missing_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        # fill with min notes and check duration to stay always monophonic
        for i, next_note in enumerate(notes[1:] + [Note(start=self.loop_end)]):
            current_note = notes[i]
            if next_note.start - current_note.end > 0:
                yield current_note
                yield Note(start=current_note.end, duration=next_note.start - current_note.end,
                           pitch=current_note.pitch, velocity=current_note.velocity)
            elif next_note.start - current_note.start == 0:
                pass
            else:
                current_note.duration = next_note.start - current_note.start
                yield current_note

    def _consolidate_notes(self, notes):
        # type: (List[Note]) -> List[Note]
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

    def _remove_start_short_notes(self, notes):
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

    def _filter_duplicate_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        " Useful to remove bug notes at same start point or when a note start was stretch to the start point of another one "
        unique_notes_by_start_and_duration = {}

        for note in notes:
            unique_notes_by_start_and_duration["%s-%s" % (note.start, note.duration)] = note

        unique_notes = unique_notes_by_start_and_duration.values()
        unique_notes.sort(key=lambda x: x.start)
        return unique_notes

    def _ramp_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        """ ramp note endings, twice faster for notes going up as clicks happen more on notes going down  """
        for i, next_note in enumerate(notes[1:] + [notes[0]]):
            current_note = notes[i]
            ramping_duration = float(self.RAMPING_DURATION) * abs(current_note.velocity - next_note.velocity) / 127
            if current_note.velocity == next_note.velocity:
                yield [current_note]
            elif next_note.velocity > current_note.velocity:
                yield self._ramp_two_notes(notes[i], next_note, ramping_duration / (2 * self.automation_ramp_up.division), self.automation_ramp_up.ramp_mode)
            else:
                yield self._ramp_two_notes(notes[i], next_note, ramping_duration / self.automation_ramp_down.division, self.automation_ramp_down.ramp_mode)

    def _ramp_two_notes(self, note, next_note, ramping_duration, ramp_mode):
        # type: (Note, Note, float, AutomationRampModeEnum) -> List[Note]
        """
            2 cases : when the note is long and ramping happens at the end
            or when the note is short and the ramping takes the whole note duration
        """
        if ramp_mode == AutomationRampModeEnum.NO_RAMP:
            yield note
            return

        is_above_ramping_duration = note.duration > ramping_duration * (1 + float(1) / self.RAMPING_STEPS)
        if is_above_ramping_duration and ramp_mode == AutomationRampModeEnum.END_RAMP:
            ramping_steps = self.RAMPING_STEPS - 1
            start_coeff = 1 - float(1) / self.RAMPING_STEPS
            ramp_start = note.start + note.duration - ramping_duration * start_coeff
            velocity_start = next_note.velocity + (note.velocity - next_note.velocity) * start_coeff
            base_duration = ramping_duration * start_coeff

            first_note = copy(note)
            first_note.duration = note.duration - ramping_duration + ramping_duration / self.RAMPING_STEPS
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


from collections import OrderedDict
from copy import copy
from fractions import Fraction
from functools import partial
from itertools import chain

import Live
from typing import List

from _Framework.SubjectSlot import subject_slot_group
from _Framework.Util import find_if
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import defer, debounce
from a_protocol_0.utils.log import set_object_attr
from a_protocol_0.utils.utils import find_last


class AutomationTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AutomationTrack, self).__init__(*a, **k)
        self.ramping_steps = 13
        self.ramping_duration = 0.25  # eighth note
        self.push2_selected_main_mode = 'clip'
        self.push2_selected_matrix_mode = 'note'
        self.push2_selected_instrument_mode = 'split_melodic_sequencer'
        self.editing_clip = None  # type: Clip

    def _added_track_init(self):
        """ this can be called once, when the Live track is created """
        if self.group_track is None:
            raise RuntimeError("An automation track should always be grouped")
        [self.delete_device(d) for d in self.devices]
        self.output_routing_type = find_if(lambda r: r.attached_object == self.group_track._track,
                                           self.available_output_routing_types)
        self.parent.defer(
            lambda: setattr(self, "output_routing_channel", find_last(lambda r: "lfotool" in r.display_name.lower(),
                                                                      self.available_output_routing_channels)))
        if len(self.clips) == 0:
            self._create_base_clips()

    @defer
    def _create_base_clips(self):
        velocity_patterns = OrderedDict()
        velocity_patterns["dry"] = lambda i: 127
        velocity_patterns["half-silent"] = lambda i: 0 if i < 4 else 127
        velocity_patterns["half-reversed"] = lambda i: 127 if i < 4 else 0
        velocity_patterns["quarter-silent"] = lambda i: 0 if i < 2 else 127

        for i, (clip_name, vel_predicate) in enumerate(velocity_patterns.items()):
            self.create_clip(slot_number=i, name=clip_name, bar_count=1, notes_callback=self._fill_equal_notes,
                             note_count=8, vel_predicate=vel_predicate)

        self.clip_slots[0]._has_clip_listener._callbacks.append(lambda: self.play())

    def _fill_equal_notes(self, clip, note_duration, note_count, vel_predicate):
        return [Note(pitch=vel_predicate(step), velocity=vel_predicate(step), start=step * note_duration,
                     duration=note_duration, clip=clip) for step
                in range(note_count)]

    @subject_slot_group("notes")
    def _clip_notes_listener(self, clip):
        # type: (Live.Clip.Clip) -> None
        self._map_notes(self.get_clip(clip))

    @debounce(7)
    def _map_notes(self, clip):
        # type: (Clip) -> None
        self.editing_clip = clip
        notes = clip.get_notes()
        if len(notes) == 0 or clip._is_updating_notes or notes == clip._notes:
            return

        self.parent.log_info("mapping notes")
        if len(clip.notes_changed(notes, ["start", "duration", "pitch"])) == 0:
            self.parent.log_info("manual pitch change")
            [setattr(note, "pitch", note.velocity) for (_, note) in clip.notes_changed(notes, ["velocity"])]
            # clip._notes = notes
            self.parent.defer(partial(self._map_notes, clip))
            return

        if len(notes) > len(clip._notes):
            clip._added_note = next(iter(list(set(notes) - set(clip._notes))), None)
            notes = list(set(notes) - set([clip._added_note]))
            notes.sort(key=lambda x: x.start)
        self.parent.log_debug("added_note : %s" % clip._added_note)
        note_transforms = [
            lambda notes: filter(lambda n: n.is_quantized, notes),
            self._insert_added_note,
            # self._remove_ramped_notes_start,
            self._consolidate_notes,
            lambda notes: list(chain(*self._ramp_note_endings(notes))),
        ]  # type: List[callable(List[Note])]

        with set_object_attr(Note, "auto_sync_enabled", False):
            for note_transform in note_transforms:
                notes = list(note_transform(notes))
                notes.sort(key=lambda x: x.start)
            [setattr(note, "pitch", note.velocity) for note in notes]

            clip.replace_all_notes(notes)

    def _insert_added_note(self, notes):
        # type: (List[Note]) -> List[Note]
        if self.editing_clip._added_note is None:
            for note in notes:
                yield note
            return

        if notes[0].start != self.editing_clip.loop_start:
            raise Exception("the first note doesn't start on clip loop start")

        i = 0
        while i < len(notes):
            note = notes[i]
            self.parent.log_debug((note, self.editing_clip._added_note.overlaps(note)))
            if not self.editing_clip._added_note.overlaps(note):
                yield note
                i += 1
                continue

            # we check only one overlap case as the added_note cannot start before the first note

            # split 1st part of the note
            if note.start != self.editing_clip._added_note.start:
                truncated_note = copy(note)
                truncated_note.duration = self.editing_clip._added_note.start - truncated_note.start
                yield truncated_note

            while self.editing_clip._added_note.end >= note.end and i < len(notes) - 1:
                i += 1
                note = notes[i]
            yield self.editing_clip._added_note
            if self.editing_clip._added_note.end < note.end:
                end = note.end
                note.start = self.editing_clip._added_note.end
                note.duration = end - note.start
                yield note

            i += 1

    def _remove_ramped_notes_start(self, notes):
        # type: (List[Note]) -> List[Note]
        """ clean ramped clip (remove un_quantized and duplicated on start notes) """
        notes_by_start = {}
        for note in notes:
            if not notes_by_start.has_key(note.start):
                notes_by_start[note.start] = note
            else:
                notes_by_start[note.start] = max([notes_by_start[note.start], note], key=lambda n: n.duration)

        return notes_by_start.values()

    def _consolidate_notes(self, notes):
        # type: (List[Note]) -> List[Note]
        # fill durations
        for i, next_note in enumerate(notes[1:] + [Note(start=self.editing_clip.length)]):
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

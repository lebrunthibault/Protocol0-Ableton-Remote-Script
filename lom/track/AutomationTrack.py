from collections import OrderedDict

import Live
from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import defer


class AutomationTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AutomationTrack, self).__init__(*a, **k)
        if len(self.clips) == 0:
            self.create_base_clips()

    @defer
    def create_base_clips(self):
        velocity_patterns = OrderedDict()
        velocity_patterns["dry"] = lambda i: 127
        velocity_patterns["half-silent"] = lambda i: 0 if i < 4 else 127
        velocity_patterns["half-reversed"] = lambda i: 127 if i < 4 else 0
        velocity_patterns["quarter-silent"] = lambda i: 0 if i < 2 else 127

        for i, (clip_name, vel_predicate) in enumerate(velocity_patterns.items()):
            self.create_clip(slot_number=i, name=clip_name, bar_count=1, notes_callback=self._fill_equal_notes, note_count=8, vel_predicate=vel_predicate)

        self.clip_slots[0]._has_clip_listener._callbacks.append(lambda: self.play())

    def _fill_equal_notes(self, clip, note_duration, note_count, vel_predicate):
        return [Note(pitch=vel_predicate(step), start=step * note_duration, duration=note_duration) for step in range(note_count)]

    @subject_slot_group("notes")
    def _clip_notes_listener(self, clip):
        # type: (Live.Clip.Clip) -> None
        clip = self.get_clip(clip)
        if clip._is_updating_notes:
            return

        self._map_notes(clip)

        def debounce_map_note():
            if clip._scheduled_note_operation_count == 1:
                self._map_notes(clip)

            clip._scheduled_note_operation_count -= 1

        self.parent._wait(2, debounce_map_note)
        clip._scheduled_note_operation_count += 1

    def _map_notes(self, clip):
        # type: (Clip) -> None
        notes = clip.get_notes()
        if len(notes) == 0:
            return
        filtered_notes = []
        last_note = None
        for note in notes:
            if len(filtered_notes) == 0:
                filtered_notes.append(note)
                continue

            last_note = filtered_notes[-1]

            if note.start == last_note.start:
                continue

            if note.start - last_note.start != last_note.duration:
                last_note._duration = note.start - last_note.start

            filtered_notes.append(note)

        last_note = filtered_notes[-1]
        if clip.length - last_note.start != last_note.duration:
            last_note._duration = clip.length - last_note.start

        [setattr(note, "_pitch", note.velocity) for note in filtered_notes]
        clip.replace_all_notes(filtered_notes)

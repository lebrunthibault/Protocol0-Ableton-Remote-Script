from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class AutomationTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AutomationTrack, self).__init__(*a, **k)
        self._fill_note_count = 8

    @subject_slot("has_clip")
    def fill_notes(self):
        clip_slot = self.get_clip_slot(self.fill_notes.subject)
        if not clip_slot or not clip_slot.has_clip:
            return
        clip = clip_slot.clip
        note_duration = clip.length / self._fill_note_count
        notes = [Note(pitch=127, start=step * note_duration, duration=note_duration) for step in
                 range(self._fill_note_count)]
        clip.replace_all_notes(notes)

    @subject_slot("notes")
    def observe_clip_notes(self):
        # type: () -> None
        clip = self.get_clip(self.observe_clip_notes.subject)
        if clip._is_updating_notes:
            return

        self._map_notes(clip)

        def debounce_map_note():
            if clip._scheduled_note_operation_count == 1:
                self.parent.log_debug("executing mapNotes")
                self._map_notes(clip);

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

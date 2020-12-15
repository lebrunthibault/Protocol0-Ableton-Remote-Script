from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class AutomationTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AutomationTrack, self).__init__(*a, **k)

    def _map_notes(self, clip):
        # type: (Clip) -> None
        notes = clip.get_notes()
        if len(notes) == 0:
            return
        filtered_notes = []
        last_note = None
        notes.sort(key=lambda x: x.start)
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

    @subject_slot("notes")
    def observe_clip_notes(self):
        # type: () -> None
        clip_slot = find_if(lambda cs: cs._clip_slot == self.song.highlighted_clip_slot, self.clip_slots)  # type: ClipSlot
        clip = clip_slot.clip
        self.parent.log_debug("observe_clip_notes called in automation")
        if clip._is_updating_notes:
            return

        self._map_notes(clip)

        def debounce_map_note():
            self.parent.log_debug(clip._scheduled_note_operation_count)
            if clip._scheduled_note_operation_count == 1:
                self.parent.log_debug("executing mapNotes")
                self._map_notes(clip);

            clip._scheduled_note_operation_count -= 1
        self.parent._wait(20, debounce_map_note)
        clip._scheduled_note_operation_count += 1

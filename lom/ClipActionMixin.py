from typing import TYPE_CHECKING, List

from _Framework.Util import find_if
from a_protocol_0.consts import push2_beat_quantization_steps
from a_protocol_0.lom.Note import Note
from a_protocol_0.utils.decorators import defer

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Clip import Clip


# noinspection PyTypeHints
class ClipActionMixin(object):
    def __init__(self):
        super(ClipActionMixin, self).__init__()
        self._is_updating_notes = False
        self._scheduled_note_operation_count = 0

    def get_notes(self, startTime=0, timeRange=0, startPitch=0, pitchRange=128):
        # type: (Clip, int, float, float, int) -> List[Note]
        notes = [Note(*note) for note in self._clip.get_notes(startTime, startPitch, timeRange or self.length, pitchRange)]
        notes.sort(key=lambda x: x.start)
        return notes

    def get_selected_notes(self):
        # type: (Clip) -> None
        return [Note(*note) for note in self._clip.get_selected_notes()]

    @defer
    def replace_selected_notes(self, notes):
        # type: (Clip, List[Note]) -> None
        self._is_updating_notes = True
        self._clip.replace_selected_notes(tuple(note.to_data() for note in notes))
        self.parent.defer(lambda: setattr(self, "_is_updating_notes", False))

    @defer
    def set_notes(self, notes):
        # type: (Clip, List[Note]) -> None
        self._is_updating_notes = True
        self._clip.set_notes(tuple(note.to_data() for note in notes))
        self.parent.defer(lambda: setattr(self, "_is_updating_notes", False))

    def select_all_notes(self):
        # type: (Clip) -> None
        self._clip.select_all_notes()

    def replace_all_notes(self, notes):
        # type: (Clip) -> None
        self.select_all_notes()
        self.replace_selected_notes(notes)

    @property
    def min_note_quantization_start(self):
        # type: (Clip) -> float
        notes = self.get_notes()
        if not len(notes):
            return 1
        notes_start_quantization = [find_if(lambda qtz: float(note.start / qtz).is_integer(), reversed(push2_beat_quantization_steps)) for note in notes]
        if None in notes_start_quantization:
            return push2_beat_quantization_steps[3]  # 1/16 by default
        else:
            return min(notes_start_quantization)

    def delete(self):
        # type: (Clip) -> None
        self._clip_slot.delete_clip()
        if self.is_recording:
            qz = self.track.song.clip_trigger_quantization
            self.track.song.clip_trigger_quantization = 0
            self.track.stop()

            def delete_recording_clip():
                self.delete()
                self.track.song.clip_trigger_quantization = qz

            self.track.parent.defer(delete_recording_clip)

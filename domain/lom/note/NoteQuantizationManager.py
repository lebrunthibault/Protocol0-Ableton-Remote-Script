from typing import List, Optional, cast, Any

from protocol0.domain.lom.note.Note import Note
from protocol0.shared.constants import PUSH2_BEAT_QUANTIZATION_STEPS


class NoteQuantizationManager(object):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(NoteQuantizationManager, self).__init__(*a, **k)
        self._steps = [v * 4 for v in PUSH2_BEAT_QUANTIZATION_STEPS]
        self._default_index = 3

    def _get_note_quantization_index(self, note):
        # type: (Note) -> Optional[int]
        for step in reversed(self._steps):
            if round(note.start / step, 6).is_integer():
                return self._steps.index(step)
        return None

    def get_notes_quantization_index(self, notes):
        # type: (List[Note]) -> int
        notes_quantization_index = [self._get_note_quantization_index(note) for note in notes]
        if len(notes_quantization_index) == 0 or None in notes_quantization_index:
            return self._default_index  # 1/16 by default
        else:
            return max(cast(List[int], notes_quantization_index))

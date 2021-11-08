from __future__ import division

from functools import partial

from typing import List, TYPE_CHECKING, Optional, Callable, Any, Iterator

import Live
from protocol0.enums.PixelEnum import PixelEnum
from protocol0.lom.Note import Note
from protocol0.lom.clip.Clip import Clip
from protocol0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack


class MidiClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MidiClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleMidiTrack
        # NOTES
        self._cached_notes = []

    def get_notes(self):
        # type: () -> List[Note]
        if not self._clip:
            return []
        # noinspection PyArgumentList
        clip_notes = [Note(*note, clip=self) for note in self._clip.get_notes(self.loop_start, 0, self.length, 128)]
        notes = list(self._get_notes_from_cache(notes=clip_notes))
        notes.sort(key=lambda x: x.start)
        return notes

    def _get_notes_from_cache(self, notes):
        # type: (List[Note]) -> Iterator[Note]
        for note in notes:
            yield next((cached_note for cached_note in self._cached_notes if cached_note == note), note)

    def _change_clip_notes(self, method, notes):
        # type: (Callable, List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        self._cached_notes = notes
        seq = Sequence(silent=True)
        seq.add(partial(method, tuple(note.to_data() for note in notes)))
        # noinspection PyUnresolvedReferences
        seq.add(wait=1)
        return seq.done()

    def set_notes(self, notes):
        # type: (List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        return self._change_clip_notes(self._clip.set_notes, notes)

    @property
    def quantization_index(self):
        # type: () -> int
        return self.parent.quantizationManager.get_notes_quantization_index(self.get_notes())

    def configure_new_clip(self):
        # type: () -> Optional[Sequence]
        if len(self.get_notes()) > 0 or self.is_recording:
            self.parent.navigationManager.show_clip_view()
            return None

        self.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth
        seq = Sequence(silent=True)
        seq.add(wait=1)
        seq.add(self.generate_base_notes)
        seq.add(self.hide_envelope)
        seq.add(wait=10, silent=True)
        seq.add(
            partial(self.system.double_click, *PixelEnum.FOLD_CLIP_NOTES.coordinates)
        )
        return seq.done()

    def generate_base_notes(self):
        # type: () -> Optional[Sequence]
        if self.track.instrument:
            return self.set_notes(self.track.instrument.generate_base_notes(self))
        else:
            return None

    def post_record(self):
        # type: () -> None
        super(MidiClip, self).post_record()
        self.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth
        self.show_loop()
        self.quantize()
        self.scale_velocities(go_next=False, scaling_factor=2)

    def scale_velocities(self, go_next, scaling_factor):
        # type: (bool, int) -> None
        notes = self.get_notes()
        if len(notes) == 0:
            return
        average_velo = sum([note.velocity for note in notes]) / len(notes)
        for note in notes:
            velocity_diff = note.velocity - average_velo
            if go_next:
                note.velocity += velocity_diff / (scaling_factor - 1)
            else:
                note.velocity -= velocity_diff / scaling_factor
        self.set_notes(notes)

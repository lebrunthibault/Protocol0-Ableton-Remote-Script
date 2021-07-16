from functools import partial

import Live
from typing import List, TYPE_CHECKING, Optional, Callable, Any

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
        # storing notes for note change comparison
        self._muted_notes = []  # type: List[Note]  # keeping this separate

    def get_notes(self, exclude_muted=True):
        # type: (bool) -> List[Note]
        if not self._clip:
            return []
        notes = [Note(*note, clip=self) for note in self._clip.get_notes(self.loop_start, 0, self.length, 128)]
        self._muted_notes = [note for note in notes if note.muted]
        if exclude_muted:
            notes = [note for note in notes if not note.muted]

        notes.sort(key=lambda x: x.start)
        return notes

    def _change_clip_notes(self, method, notes):
        # type: (Callable, List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        notes += [note for note in self._muted_notes if note.start == 0]  # reintegrating muted notes
        seq = Sequence(silent=True)
        seq.add(partial(method, tuple(note.to_data() for note in notes)))
        # noinspection PyUnresolvedReferences
        seq.add(self.notify_notes)  # for automation audio track to be notified
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
        self.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth

        if len(self.get_notes()) > 0:
            self.play()
            self.parent.navigationManager.show_clip_view()
            return None

        seq = Sequence(silent=True)
        seq.add(wait=1)
        seq.add(self.generate_base_notes)
        seq.add(self.hide_envelope)
        seq.add(wait=10, silent=True)
        seq.add(
            partial(self.system.double_click, PixelEnum.FOLD_CLIP_NOTES.value[0], PixelEnum.FOLD_CLIP_NOTES.value[1])
        )
        return seq.done()

    def generate_base_notes(self):
        # type: () -> Optional[Sequence]
        """ Generate base clip notes on clip creation, overridden"""
        if self.track.instrument:
            return self.set_notes(self.track.instrument.generate_base_notes(self))
        else:
            return None

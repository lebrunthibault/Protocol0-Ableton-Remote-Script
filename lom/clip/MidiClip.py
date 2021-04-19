import itertools
from functools import partial

import Live
from typing import List, TYPE_CHECKING, Optional, Callable, Tuple, Any

from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import have_equal_properties

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack


class MidiClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MidiClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleMidiTrack
        # NOTES
        # storing notes for note change comparison
        self._muted_notes = []  # type: List[Note]  # keeping this separate
        self._prev_notes = self.get_notes()  # type: List[Note]
        self._added_note = None  # type: Optional[Note]
        self._is_updating_notes = False

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

    def _change_clip_notes(self, method, notes, cache=True):
        # type: (Callable, List[Note], bool) -> Optional[Sequence]
        if not self._clip:
            return None
        self._is_updating_notes = True
        if cache:
            self._prev_notes = [note for note in notes if not note.muted]
        notes += [note for note in self._muted_notes if note.start == 0]  # reintegrating muted notes
        seq = Sequence(silent=True)
        seq.add(partial(method, tuple(note.to_data() for note in notes)))
        # noinspection PyUnresolvedReferences
        seq.add(self.notify_notes)  # for automation audio track to be notified
        seq.add(wait=1)
        seq.add(lambda: setattr(self, "_is_updating_notes", False))
        return seq.done()

    def _replace_selected_notes(self, notes):
        # type: (List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        return self._change_clip_notes(self._clip.replace_selected_notes, notes)

    def set_notes(self, notes):
        # type: (List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        return self._change_clip_notes(self._clip.set_notes, notes, cache=False)

    def _select_all_notes(self):
        # type: () -> None
        if not self._clip:
            return None
        self._clip.select_all_notes()

    def _deselect_all_notes(self):
        # type: () -> None
        if not self._clip:
            return
        self._clip.deselect_all_notes()
        self.parent.clyphxNavigationManager.show_clip_view()
        self.view.show_loop()

    def replace_all_notes(self, notes):
        # type: (List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        self._select_all_notes()
        seq = Sequence(silent=True)
        seq.add(wait=1)
        seq.add(partial(self._replace_selected_notes, notes))
        seq.add(self._deselect_all_notes)
        return seq.done()

    def notes_changed(self, notes, checked_properties, prev_notes=None):
        # type: (List[Note], List[str], List[Note]) -> List[Tuple[Note, Note]]
        prev_notes = prev_notes or self._prev_notes
        all_properties = ["start", "duration", "pitch", "velocity"]
        excluded_properties = list(set(all_properties) - set(checked_properties))
        if len(prev_notes) != len(notes):
            return []

        changed_notes = []  # type: List[Tuple[Note, Note]]
        # keeping only those who have the same excluded properties and at least one checked_property change
        for prev_note, note in itertools.izip(prev_notes, notes):  # type: ignore[attr-defined]
            if have_equal_properties(prev_note, note, excluded_properties) and not have_equal_properties(
                prev_note, note, checked_properties
            ):
                changed_notes.append((prev_note, note))

        return changed_notes

    @property
    def quantization_index(self):
        # type: () -> int
        return self.parent.quantizationManager.get_notes_quantization_index(self.get_notes())

    def configure_new_clip(self):
        # type: () -> Optional[Sequence]
        self.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth

        if len(self.get_notes()) > 0:
            self.play()
            self.parent.clyphxNavigationManager.show_clip_view()
            return None

        seq = Sequence()
        seq.add(partial(self.replace_all_notes, self.generate_base_notes()))
        seq.add(self.view.hide_envelope, silent=True)
        seq.add(wait=10, silent=True)
        seq.add(self.parent.keyboardShortcutManager.click_clip_fold)
        return seq.done()

    def generate_base_notes(self):
        # type: (Clip) -> List[Note]
        """ Generate base clip notes on clip creation, overridden"""
        if self.track.instrument:
            return self.track.instrument.generate_base_notes(self)
        else:
            return []

from functools import partial
from typing import List, TYPE_CHECKING

import Live

from _Framework.Util import find_if
from a_protocol_0.consts import PUSH2_BEAT_QUANTIZATION_STEPS
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import have_equal_properties
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.Clip import Clip

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack


class MidiClip(Clip):
    def __init__(self, *a, **k):
        super(MidiClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleMidiTrack
        # NOTES
        # storing notes for note change comparison
        self._muted_notes = []  # type: List[Note]  # keeping this separate
        self._prev_notes = self.get_notes()  # type: List[Note]
        self._added_note = None  # type: Note
        self._is_updating_notes = False

    def get_notes(self, exclude_muted=True):
        # type: (bool) -> List[Note]
        if not self._clip:
            return []
        notes = [Note(*note, clip=self) for note in
                 self._clip.get_notes(self.loop_start, 0, self.length, 128)]
        self._muted_notes = [note for note in notes if note.muted]
        if exclude_muted:
            notes = [note for note in notes if not note.muted]

        notes.sort(key=lambda x: x.start)
        return notes

    def _change_clip_notes(self, method, notes, cache=True):
        # type: (callable, List[Note], bool) -> Sequence
        if not self._clip:
            return
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
        # type: (List[Note]) -> Sequence
        if not self._clip:
            return
        return self._change_clip_notes(self._clip.replace_selected_notes, notes)

    def set_notes(self, notes):
        # type: (List[Note]) -> Sequence
        if not self._clip:
            return
        return self._change_clip_notes(self._clip.set_notes, notes, cache=False)

    def _select_all_notes(self):
        if not self._clip:
            return
        self._clip.select_all_notes()

    def _deselect_all_notes(self):
        if not self._clip:
            return
        self._clip.deselect_all_notes()
        self.parent.clyphxNavigationManager.show_clip_view()
        self.view.show_loop()

    def replace_all_notes(self, notes):
        # type: (List[Note]) -> None
        if not self._clip:
            return
        self._select_all_notes()
        seq = Sequence(silent=True)
        seq.add(wait=1)
        seq.add(partial(self._replace_selected_notes, notes))
        seq.add(self._deselect_all_notes)
        return seq.done()

    def notes_changed(self, notes, checked_properties, prev_notes=None):
        # type: (Clip, List[Note], List[str]) -> List[Note]
        prev_notes = prev_notes or self._prev_notes
        all_properties = ["start", "duration", "pitch", "velocity"]
        excluded_properties = list(set(all_properties) - set(checked_properties))
        if len(prev_notes) != len(notes):
            return []

        # keeping only those who have the same excluded properties and at least one checked_property change
        return list(filter(None,
                           map(lambda x, y: None if not have_equal_properties(x, y,
                                                                              excluded_properties) or have_equal_properties(
                               x, y, checked_properties) else (x, y), prev_notes,
                               notes)))

    @property
    def min_note_quantization_start(self):
        # type: () -> float
        notes = self.get_notes()
        if not len(notes):
            return 1
        notes_start_quantization = [
            find_if(lambda qtz: float(note.start / qtz).is_integer(), reversed(PUSH2_BEAT_QUANTIZATION_STEPS)) for note
            in notes]
        if None in notes_start_quantization:
            return PUSH2_BEAT_QUANTIZATION_STEPS[3]  # 1/16 by default
        else:
            return min(notes_start_quantization)

    def configure_new_clip(self):
        self.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth

        if len(self.get_notes()) > 0:
            self.play()
            self.parent.clyphxNavigationManager.show_clip_view()
            return

        seq = Sequence()
        seq.add(partial(self.replace_all_notes, self.generate_base_notes()))
        seq.add(self.view.hide_envelope, silent=True)
        seq.add(wait=10, silent=True)
        seq.add(self.parent.keyboardShortcutManager.click_clip_fold)
        return seq.done()

    def generate_base_notes(self):
        # type: (Clip) -> None
        """ Generate base clip notes on clip creation, overridden"""
        if self.track.instrument:
            return self.track.instrument.generate_base_notes(self)
        else:
            return []

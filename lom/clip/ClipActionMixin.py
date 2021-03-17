from functools import partial

import Live
from typing import TYPE_CHECKING, List

from _Framework.Util import find_if
from a_protocol_0.consts import PUSH2_BEAT_QUANTIZATION_STEPS, RECORD_QUANTIZE_NAMES
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import is_change_deferrable
from a_protocol_0.utils.utils import have_equal_properties

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip.Clip import Clip


# noinspection PyTypeHints
class ClipActionMixin(object):
    def select(self):
        # type: (Clip) -> None
        self.song.highlighted_clip_slot = self.clip_slot
        seq = Sequence(silent=True)
        seq.add(wait=2)
        seq.add(self.parent.clyphxNavigationManager.show_clip_view)
        return seq.done()

    def play(self):
        # type: (Clip) -> None
        if self._clip:
            self.is_playing = True

    def get_notes(self, exclude_muted=True):
        # type: (Clip, bool) -> List[Note]
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
        # type: (Clip, callable, List[Note], bool) -> Sequence
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
        # type: (Clip, List[Note], bool) -> Sequence
        if not self._clip:
            return
        return self._change_clip_notes(self._clip.replace_selected_notes, notes)

    def set_notes(self, notes):
        # type: (Clip, List[Note]) -> Sequence
        if not self._clip:
            return
        return self._change_clip_notes(self._clip.set_notes, notes, cache=False)

    def _select_all_notes(self):
        # type: (Clip) -> None
        if not self._clip:
            return
        self._clip.select_all_notes()

    def _deselect_all_notes(self):
        # type: (Clip) -> None
        if not self._clip:
            return
        self._clip.deselect_all_notes()
        self.parent.clyphxNavigationManager.show_clip_view()
        self.view.show_loop()

    def replace_all_notes(self, notes):
        # type: (Clip, List[Note], bool) -> None
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
                           map(lambda x, y: None if not have_equal_properties(x, y, excluded_properties) or have_equal_properties(x, y, checked_properties) else (x, y), prev_notes,
                               notes)))

    @property
    def min_note_quantization_start(self):
        # type: (Clip) -> float
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

    def delete(self):
        # type: (Clip) -> None
        if not self._clip:
            return
        seq = Sequence()
        if self.is_recording:
            return
            # self.track.stop(immediate=True)

        seq.add(self.clip_slot.delete_clip, complete_on=self.clip_slot._has_clip_listener)

        if self.is_recording:
            seq.add(self.delete)

        return seq.done()

    def create_automation_envelope(self, parameter):
        # type: (Clip, DeviceParameter) -> Live.Clip.AutomationEnvelope
        if parameter is None:
            raise Protocol0Error("You passed None to Clip.create_automation_envelope for clip %s" % self)
        return self._clip.create_automation_envelope(parameter._device_parameter)

    def clear_all_envelopes(self):
        # type: (Clip) -> None
        if self._clip:
            return self._clip.clear_all_envelopes()

    @is_change_deferrable
    def quantize(self, quantization='1/16', depth=1):
        # type: (Clip, str, float) -> None
        if self._clip:
            rate = RECORD_QUANTIZE_NAMES.index(quantization)
            self._clip.quantize(rate, depth)


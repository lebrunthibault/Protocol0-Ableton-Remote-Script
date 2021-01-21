from functools import partial

import Live
from typing import TYPE_CHECKING, List

from _Framework.Util import find_if
from a_protocol_0.consts import push2_beat_quantization_steps
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import compare_properties

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip.Clip import Clip


# noinspection PyTypeHints
class ClipActionMixin(object):
    def get_notes(self, startTime=0, timeRange=0, startPitch=0, pitchRange=128):
        # type: (Clip, int, float, float, int) -> List[Note]
        notes = [Note(*note, clip=self) for note in
                 self._clip.get_notes(startTime, startPitch, timeRange or self.length, pitchRange)]
        notes.sort(key=lambda x: x.start)
        return notes

    def get_selected_notes(self):
        # type: (Clip) -> None
        return [Note(*note, clip=self) for note in self._clip.get_selected_notes()]

    def _change_clip_notes(self, method, notes, cache=True):
        # type: (Clip, callable, List[Note], bool) -> Sequence
        self._is_updating_notes = True
        if cache:
            self._prev_notes = notes
        seq = Sequence()
        seq.add(wait=1)
        seq.add(partial(method, tuple(note.to_data() for note in notes)))
        seq.add(lambda: setattr(self, "_is_updating_notes", False))
        # noinspection PyUnresolvedReferences
        seq.add(self.notify_notes)  # for automation audio track to be notified
        return seq.done()

    def replace_selected_notes(self, notes, cache=True):
        # type: (Clip, List[Note], bool) -> Sequence
        return self._change_clip_notes(self._clip.replace_selected_notes, notes, cache=cache)

    def set_notes(self, notes):
        # type: (Clip, List[Note]) -> Sequence
        return self._change_clip_notes(self._clip.set_notes, notes, cache=False)

    def select_all_notes(self):
        # type: (Clip) -> None
        self._clip.select_all_notes()

    def deselect_all_notes(self):
        # type: (Clip) -> None
        self._clip.deselect_all_notes()

    def replace_all_notes(self, notes, cache=True):
        # type: (Clip, List[Note], bool) -> None
        self.select_all_notes()
        new_clip = not len(self._prev_notes)
        seq = Sequence()
        seq.add(partial(self.replace_selected_notes, notes, cache=cache))
        seq.add(self.deselect_all_notes)
        return seq.done()

    def notes_changed(self, notes, properties):
        # type: (Clip, List[Note], List[str]) -> List[Note]
        if len(self._prev_notes) != len(notes):
            return notes
        return list(filter(None,
                           map(lambda x, y: None if compare_properties(x, y, properties) else (x, y), self._prev_notes,
                               notes)))

    @property
    def min_note_quantization_start(self):
        # type: (Clip) -> float
        notes = self.get_notes()
        if not len(notes):
            return 1
        notes_start_quantization = [
            find_if(lambda qtz: float(note.start / qtz).is_integer(), reversed(push2_beat_quantization_steps)) for note
            in notes]
        if None in notes_start_quantization:
            return push2_beat_quantization_steps[3]  # 1/16 by default
        else:
            return min(notes_start_quantization)

    def delete(self):
        # type: (Clip) -> None
        if not self._clip:
            return
        seq = Sequence()
        if self.is_recording:
            qz = self.track.song.clip_trigger_quantization
            self.track.song.clip_trigger_quantization = 0
            self.track.stop()

        seq.add(self._clip_slot.delete_clip, complete_on=self.clip_slot._has_clip_listener)
        if self.is_recording:
            seq.add(self.delete)
            seq.add(setattr(self.track.song, "clip_trigger_quantization", qz))

        return seq.done()

    def create_automation_envelope(self, parameter):
        # type: (Clip, DeviceParameter) -> Live.Clip.AutomationEnvelope
        if parameter is None:
            raise Protocol0Error("You passed None to Clip.create_automation_envelope")
        return self._clip.create_automation_envelope(parameter._device_parameter)

    def clear_all_envelopes(self):
        # type: (Clip) -> None
        return self._clip.clear_all_envelopes()

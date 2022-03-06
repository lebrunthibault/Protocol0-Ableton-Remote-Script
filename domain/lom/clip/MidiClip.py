from __future__ import division

from functools import partial

from typing import List, TYPE_CHECKING, Optional, Iterator

import Live
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device_parameter.LinkedDeviceParameters import LinkedDeviceParameters
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.shared.utils import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
    from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot


class MidiClip(Clip):
    def __init__(self, clip_slot):
        # type: (MidiClipSlot) -> None
        super(MidiClip, self).__init__(clip_slot)
        self.track = self.track  # type: SimpleMidiTrack
        self.clip_slot = self.clip_slot  # type: MidiClipSlot
        # NOTES
        self._cached_notes = []

    def hash(self):
        # type: () -> int
        return hash(tuple(note.to_data() for note in self.get_notes()))

    def get_notes(self):
        # type: () -> List[Note]
        if not self._clip:
            return []
        # noinspection PyArgumentList
        clip_notes = [Note(*note) for note in self._clip.get_notes(self.loop_start, 0, self.length, 128)]
        notes = list(self._get_notes_from_cache(notes=clip_notes))
        notes.sort(key=lambda x: x.start)
        return notes

    def _get_notes_from_cache(self, notes):
        # type: (List[Note]) -> Iterator[Note]
        for note in notes:
            yield next((cached_note for cached_note in self._cached_notes if cached_note == note), note)

    def set_notes(self, notes):
        # type: (List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        self._cached_notes = notes
        self._clip.get_selected_notes()
        seq = Sequence()
        seq.add(partial(self._clip.replace_selected_notes, tuple(note.to_data() for note in notes)))
        # noinspection PyUnresolvedReferences
        seq.defer()
        return seq.done()

    def configure_new_clip(self):
        # type: () -> Optional[Sequence]
        if len(self.get_notes()) > 0 or self.is_recording:
            return None

        self.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth
        seq = Sequence()
        seq.defer()
        seq.add(self.generate_base_notes)
        seq.wait(10)
        return seq.done()

    def generate_base_notes(self):
        # type: () -> Optional[Sequence]
        if self.track.instrument:
            base_notes = [Note(pitch=60, velocity=127, start=0, duration=min(1, int(self.length)))]
            return self.set_notes(base_notes)
        else:
            return None

    def post_record(self, bar_length):
        # type: (int) -> None
        super(MidiClip, self).post_record(bar_length)
        if bar_length == 0:  # unlimited recording
            clip_end = int(self.end_marker) - (int(self.end_marker) % SongFacade.signature_numerator())
            self.loop_end = clip_end
            self.end_marker = clip_end

        self.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth
        self.scale_velocities(go_next=False, scaling_factor=2)
        self.quantize()

    def scale_velocities(self, go_next, scaling_factor=4):
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

    def crop(self):
        # type: () -> None
        if self._clip:
            self._clip.crop()

    def get_linked_parameters(self):
        # type: () -> List[LinkedDeviceParameters]
        """
            NB : this is only really useful for my rev2 where I want copy paste easily automation curves
            between the 2 layers.
            The rev2 is bitimbral and has two layers that expose the same parameters.
        """
        parameters = self.automated_parameters
        parameters_couple = []
        for parameter in parameters:
            if parameter.name.startswith("A-"):
                b_parameter = find_if(lambda p: p.name == parameter.name.replace("A-", "B-"), parameters)
                if b_parameter:
                    parameters_couple.append(LinkedDeviceParameters(parameter, b_parameter))

        return parameters_couple

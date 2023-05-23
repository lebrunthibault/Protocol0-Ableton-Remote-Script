from __future__ import division

from functools import partial

import Live
from typing import List, Optional, Iterator, Any

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.device_parameter.LinkedDeviceParameters import LinkedDeviceParameters
from protocol0.domain.lom.instrument.instrument.InstrumentSimpler import InstrumentSimpler
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class MidiClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MidiClip, self).__init__(*a, **k)
        self._cached_notes = []  # type: List[Note]

        # select when a new midi clip is recorded
        if self.is_recording:
            Scheduler.defer(self.select)

    def get_hash(self, device_parameters):
        # type: (List[DeviceParameter]) -> int
        midi_hash = hash(tuple(note.to_data() for note in self.get_notes()))

        return hash((midi_hash, self.automation.get_hash(device_parameters)))

    @property
    def starts_at_1(self):
        # type: () -> bool
        return any(note.start == 0 for note in self.get_notes())

    def get_notes(self):
        # type: () -> List[Note]
        if not self._clip:
            return []

        # noinspection PyArgumentList,PyUnresolvedReferences
        clip_notes = [
            # Note(*note) for note in self._clip.get_notes(self.loop.start, 0, self.length, 128)
            Note.from_midi_note(note)
            for note in self._clip.get_notes_extended(0, 128, self.loop.start, self.length)
        ]

        notes = list(self._get_notes_from_cache(notes=clip_notes))
        notes.sort(key=lambda x: x.start)
        return notes

    def _get_notes_from_cache(self, notes):
        # type: (List[Note]) -> Iterator[Note]
        for note in notes:
            yield next(
                (cached_note for cached_note in self._cached_notes if cached_note == note), note
            )

    def set_notes(self, notes):
        # type: (List[Note]) -> Optional[Sequence]
        if not self._clip:
            return None
        self._cached_notes = notes
        self._clip.select_all_notes()  # noqa
        seq = Sequence()
        seq.add(partial(self._clip.replace_selected_notes, tuple(note.to_data() for note in notes)))
        # noinspection PyUnresolvedReferences
        seq.defer()
        return seq.done()

    def on_added(self):
        # type: () -> Optional[Sequence]
        if len(self.get_notes()) > 0 or self.is_recording:
            return None

        self._clip.view.grid_quantization = Live.Clip.GridQuantization.g_eighth

        seq = Sequence()
        seq.defer()
        seq.add(partial(setattr, self, "length", Song.selected_scene().length))
        seq.add(partial(setattr, self._clip, "end_marker", Song.selected_scene().length))
        seq.add(self.show_loop)

        if isinstance(Song.selected_track().instrument, InstrumentSimpler):
            seq.add(self.generate_base_notes)
            seq.wait(10)

        return seq.done()

    def generate_base_notes(self):
        # type: () -> Optional[Sequence]
        self.show_loop()

        pitch = self._config.default_note
        base_notes = [Note(pitch=pitch, velocity=127, start=0, duration=min(1, int(self.length)))]
        return self.set_notes(base_notes)

    def post_record(self, bar_length):
        # type: (int) -> None
        super(MidiClip, self).post_record(bar_length)

        if bar_length == 0:  # unlimited recording
            clip_end = int(self.loop.end) - (int(self.loop.end) % Song.signature_numerator())
            self.loop.end = clip_end

        self._clip.view.grid_quantization = Live.Clip.GridQuantization.g_eighth
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
        # type: () -> Optional[Sequence]
        if self._clip:
            self._clip.crop()  # noqa

        return None

    def to_mono(self):
        # type: () -> None
        """If notes overlap : make end of each note match the start of the next one"""
        notes = self.get_notes()

        if len(notes) < 2:
            return None

        current_note = notes[0]

        for next_note in notes[1:]:
            current_note.end = max(current_note.end, next_note.start)
            current_note = next_note

            self.set_notes(notes)

    def get_linked_parameters(self, device_parameters):
        # type: (List[DeviceParameter]) -> List[LinkedDeviceParameters]
        """
        NB : this is only really useful for my rev2 where I want to copy and paste easily automation curves
        between the 2 layers.
        The rev2 is bi timbral and has two layers that expose the same parameters.
        """
        automated_parameters = self.automation.get_automated_parameters(device_parameters)
        parameters_couple = []
        for automated_parameter in automated_parameters:
            if automated_parameter.name.startswith("A-"):
                b_parameter_name = automated_parameter.name.replace("A-", "B-")
                b_parameter = find_if(lambda p: p.name == b_parameter_name, device_parameters)
                assert b_parameter, "Cannot find %s" % b_parameter_name
                if b_parameter not in automated_parameters:
                    self.automation.create_envelope(b_parameter)

                parameters_couple.append(LinkedDeviceParameters(automated_parameter, b_parameter))

        return parameters_couple

    def synchronize_automation_layers(self, device_parameters):
        # type: (List[DeviceParameter]) -> Sequence
        parameters_couple = self.get_linked_parameters(device_parameters)

        Logger.info("parameters_couple: %s" % parameters_couple)

        if len(parameters_couple) == 0:
            raise Protocol0Warning("This clip has no linked automated parameters")

        Song.draw_mode(False)
        seq = Sequence()
        for couple in parameters_couple:
            seq.add(partial(couple.link_clip_automation, self.automation))

        # refocus an A parameter to avoid mistakenly modify a B one
        seq.add(partial(self.automation.show_parameter_envelope, parameters_couple[-1]._param_a))

        return seq.done()

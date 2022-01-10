from __future__ import division

from functools import partial

from typing import List, TYPE_CHECKING, Optional, Any, Iterator, cast

import Live
from protocol0.lom.Note import Note
from protocol0.lom.clip.Clip import Clip
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
    from protocol0.lom.clip_slot.MidiClipSlot import MidiClipSlot


class MidiClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MidiClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleMidiTrack
        self.clip_slot = self.clip_slot  # type: MidiClipSlot
        # NOTES
        self._cached_notes = []

    def hash(self):
        # type: () -> int
        return hash(tuple(note.to_data() for note in self.get_notes()))

    @p0_subject_slot("loop_end")
    def _loop_end_listener(self):
        # type: () -> None
        self.parent.defer(partial(setattr, self, "end_marker", self.loop_end))

        from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
        if not isinstance(self.track.abstract_track, ExternalSynthTrack):
            return
        track = cast(ExternalSynthTrack, self.track.abstract_track)
        if not track.audio_tail_track:
            return
        tail_clip = track.audio_tail_track.clip_slots[self.index].clip
        if tail_clip:
            # NB: with looping off, setting the loop actually sets the markers
            self.parent.defer(partial(setattr, tail_clip, "loop_start", self.loop_end))
            self.parent.defer(partial(setattr, tail_clip, "start_marker", self.loop_end))
            self.parent.defer(partial(setattr, tail_clip, "loop_end", self.loop_end + self.song.signature_numerator))
            self.parent.defer(partial(setattr, tail_clip, "end_marker", self.loop_end + self.song.signature_numerator))

        super(MidiClip, self)._loop_end_listener()

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
        seq.add(wait=1)
        return seq.done()

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
        seq = Sequence()
        seq.add(wait=1)
        seq.add(self.generate_base_notes)
        seq.add(self.hide_envelope)
        seq.add(wait=10)
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

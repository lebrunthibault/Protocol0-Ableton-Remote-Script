from functools import partial

from typing import List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMidiTrack(SimpleTrack):
    CLIP_SLOT_CLASS = MidiClipSlot

    @property
    def clip_slots(self):
        # type: () -> List[MidiClipSlot]
        return cast(List[MidiClipSlot], super(SimpleMidiTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[MidiClip]
        return super(SimpleMidiTrack, self).clips  # noqa

    def broadcast_selected_clip(self):
        # type: () -> Sequence
        selected_cs = Song.selected_clip_slot(MidiClipSlot)
        clip = selected_cs.clip
        if clip is None:
            raise Protocol0Warning("No selected clip")

        matching_clip_slots = [
            c
            for c in self.clip_slots
            if c.clip and c.clip.matches(clip, self.devices.parameters) and c.clip is not clip
        ]

        Backend.client().show_info("Copying to %s clips" % len(matching_clip_slots))
        seq = Sequence()
        seq.add([partial(selected_cs.duplicate_clip_to, cs) for cs in matching_clip_slots])
        return seq.done()

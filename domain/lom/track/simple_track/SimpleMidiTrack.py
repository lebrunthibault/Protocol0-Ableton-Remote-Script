from typing import List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleMidiTrack(SimpleTrack):
    DEFAULT_NAME = "midi"
    CLIP_SLOT_CLASS = MidiClipSlot

    @property
    def clip_slots(self):
        # type: () -> List[MidiClipSlot]
        return cast(List[MidiClipSlot], super(SimpleMidiTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[MidiClip]
        return super(SimpleMidiTrack, self).clips  # type: ignore

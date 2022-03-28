from typing import Any, List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleMidiTrack(SimpleTrack):
    DEFAULT_NAME = "midi"
    CLIP_SLOT_CLASS = MidiClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiTrack, self).__init__(*a, **k)
        self.clip_slots = cast(List[MidiClipSlot], self.clip_slots)

    @property
    def clips(self):
        # type: () -> List[MidiClip]
        return super(SimpleMidiTrack, self).clips  # type: ignore

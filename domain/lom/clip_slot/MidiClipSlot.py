from typing import Any, Optional

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot


class MidiClipSlot(ClipSlot):
    CLIP_CLASS = MidiClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MidiClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[MidiClip]

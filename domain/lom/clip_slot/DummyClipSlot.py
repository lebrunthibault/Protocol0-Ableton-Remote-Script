from typing import Optional, Any

from protocol0.domain.lom.clip.DummyClip import DummyClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot


class DummyClipSlot(AudioClipSlot):
    CLIP_CLASS = DummyClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(DummyClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[DummyClip]

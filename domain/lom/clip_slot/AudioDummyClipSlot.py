from typing import Optional, Any

from protocol0.domain.lom.clip.AudioDummyClip import AudioDummyClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot


class AudioDummyClipSlot(AudioClipSlot):
    CLIP_CLASS = AudioDummyClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioDummyClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioDummyClip]

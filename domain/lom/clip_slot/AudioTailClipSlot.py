from typing import Optional, Any

from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot


class AudioTailClipSlot(AudioClipSlot):
    CLIP_CLASS = AudioTailClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioTailClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioTailClip]

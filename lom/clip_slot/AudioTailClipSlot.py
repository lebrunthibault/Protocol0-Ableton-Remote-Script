from typing import Any, Optional

from protocol0.lom.clip.AudioTailClip import AudioTailClip
from protocol0.lom.clip_slot.AudioClipSlot import AudioClipSlot


class AudioTailClipSlot(AudioClipSlot):
    CLIP_CLASS = AudioTailClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioTailClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioTailClip]

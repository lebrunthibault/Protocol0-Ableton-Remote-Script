from typing import Optional

from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot


class AudioTailClipSlot(AudioClipSlot):
    CLIP_CLASS = AudioTailClip

    def __init__(self):
        # type: () -> None
        super(AudioTailClipSlot, self).__init__()
        self.clip = self.clip  # type: Optional[AudioTailClip]

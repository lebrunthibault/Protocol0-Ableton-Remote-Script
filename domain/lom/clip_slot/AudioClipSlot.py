from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.shared.sequence.Sequence import Sequence


class AudioClipSlot(ClipSlot):
    CLIP_CLASS = AudioClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioClip]
        self.previous_audio_file_path = None  # type: Optional[str]
        if self.clip:
            self.previous_audio_file_path = self.clip.file_path

    def delete_clip(self):
        # type: () -> Sequence
        if self.clip:
            self.previous_audio_file_path = self.clip.file_path
        return super(AudioClipSlot, self).delete_clip()

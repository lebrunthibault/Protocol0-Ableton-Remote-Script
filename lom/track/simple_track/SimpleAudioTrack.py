from typing import List, Any

from protocol0.enums.ColorEnum import ColorEnum
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleAudioTrack(SimpleTrack):
    DEFAULT_NAME = "audio"
    DEFAULT_COLOR = ColorEnum.DEFAULT
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        self.clip_slots = self.clip_slots  # type: List[AudioClipSlot]

    @property
    def clips(self):
        # type: () -> List[AudioClip]
        return super(SimpleAudioTrack, self).clips  # type: ignore

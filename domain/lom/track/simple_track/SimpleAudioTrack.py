from typing import List, cast

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleAudioTrack(SimpleTrack):
    DEFAULT_NAME = "audio"
    CLIP_SLOT_CLASS = AudioClipSlot

    @property
    def clip_slots(self):
        # type: () -> List[AudioClipSlot]
        return cast(List[AudioClipSlot], super(SimpleAudioTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioClip]
        return cast(List[AudioClip], super(SimpleAudioTrack, self).clips)

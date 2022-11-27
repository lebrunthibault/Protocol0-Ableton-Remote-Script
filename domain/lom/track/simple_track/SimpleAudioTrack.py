from typing import List, cast, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    @property
    def clip_slots(self):
        # type: () -> List[AudioClipSlot]
        return cast(List[AudioClipSlot], super(SimpleAudioTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioClip]
        return cast(List[AudioClip], super(SimpleAudioTrack, self).clips)

    @property
    def playing_clip(self):
        # type: () -> Optional[AudioClip]
        return super(SimpleAudioTrack, self).playing_clip

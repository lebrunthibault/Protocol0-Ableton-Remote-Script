from typing import List

from protocol0.enums.ColorEnum import ColorEnum
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleAudioTrack(SimpleTrack):
    DEFAULT_NAME = "audio"
    DEFAULT_COLOR = ColorEnum.DEFAULT
    CLIP_CLASS = AudioClip

    @property
    def clips(self):
        # type: () -> List[AudioClip]
        return super(SimpleAudioTrack, self).clips  # type: ignore

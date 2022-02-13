from typing import TYPE_CHECKING

from protocol0.domain.lom.clip.AudioClip import AudioClip

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
    from protocol0.domain.lom.clip_slot.AudioDummyClipSlot import AudioDummyClipSlot


class AudioDummyClip(AudioClip):
    def __init__(self, clip_slot):
        # type: (AudioDummyClipSlot) -> None
        super(AudioDummyClip, self).__init__(clip_slot)
        self.track = self.track  # type: SimpleDummyTrack
        self.clip_slot = self.clip_slot  # type: AudioDummyClipSlot

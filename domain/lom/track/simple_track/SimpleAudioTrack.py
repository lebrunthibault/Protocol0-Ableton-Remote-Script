from typing import List, cast, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
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

    def has_same_clips(self, track):
        # type: (AbstractTrack) -> bool
        if not isinstance(track, SimpleAudioTrack):
            return False

        return all(clip.matches(other_clip) for clip, other_clip in zip(self.clips, track.clips))

    def fix_flattened_clips(self):
        # type: () -> None
        for clip in self.clips:
            clip.loop.start = clip.loop._clip.start_marker
            clip.crop()

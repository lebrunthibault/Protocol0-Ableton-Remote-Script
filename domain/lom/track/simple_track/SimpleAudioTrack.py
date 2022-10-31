from typing import List, cast, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger


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

    def stop(self, scene_index=None, next_scene_index=None, immediate=False):
        # type: (Optional[int], Optional[int], bool) -> None
        """
        Will stop the track immediately or quantized
        the scene_index is useful for fine tuning the stop of abstract group tracks
        """
        if scene_index is None or immediate:
            return super(SimpleAudioTrack, self).stop(scene_index, next_scene_index, immediate)

        # let tail play
        clip = self.clip_slots[scene_index].clip
        if clip is not None and clip.is_playing:
            Logger.dev((self, clip.playing_position.bars_left))
            Scheduler.wait_bars(clip.playing_position.bars_left, clip.stop)

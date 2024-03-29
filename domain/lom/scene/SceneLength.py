from typing import Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.shared.utils.utils import previous_power_of_2
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class SceneLength(object):
    def __init__(self, clips, scene_index):
        # type: (SceneClips, int) -> None
        self._clips = clips
        self._scene_index = scene_index

    def __repr__(self):
        # type: () -> str
        return "SceneLength(index=%s, length=%f)" % (self._scene_index, self.length)

    @property
    def _is_playing(self):
        # type: () -> bool
        return any(clip.is_playing for clip in self._clips)

    @property
    def length(self):
        # type: () -> float
        longest_clip = self.get_longest_clip(
            is_playing=True) if self._is_playing else self.get_longest_clip()
        clip_length = longest_clip.length if longest_clip else 0.0
        numerator = Song.signature_numerator()

        if clip_length % numerator != 0:
            return clip_length

        # check for tails and floor to 2^x
        return previous_power_of_2(int(clip_length / numerator)) * numerator

    @property
    def bar_length(self):
        # type: () -> int
        if self.length % Song.signature_numerator() != 0:
            # can happen when changing the longest clip length
            Logger.warning("%s invalid length: %s" % (self, self.length))
        return int(self.length / Song.signature_numerator())

    def get_longest_clip(self, is_playing=False):
        # type: (bool) -> Optional[Clip]
        """
            We take any clip except
            - recording clips that have a non integer length
            - muted clips

        We cannot exclude all recording clips in the case the midi clip is the longest
        and we are recording audio
        """

        clips = [
            clip
            for clip in self._clips
            if (not clip.is_recording or float(clip.length).is_integer())
               and not is_playing or clip.is_playing
               and not clip.muted
        ]
        if len(clips) == 0:
            return None
        else:
            return max(clips, key=lambda c: c.length)

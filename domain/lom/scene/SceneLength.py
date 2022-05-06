from typing import Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class SceneLength(object):
    def __init__(self, clips):
        # type: (SceneClips) -> None
        self._clips = clips

    @property
    def length(self):
        # type: () -> float
        return self._longest_clip.length if self._longest_clip else 0

    @property
    def bar_length(self):
        # type: () -> int
        if self.length % SongFacade.signature_numerator() != 0:
            # can happen when changing the longest clip length
            Logger.warning("%s invalid length: %s" % (self, self.length))
        return int(self.length / SongFacade.signature_numerator())

    @property
    def _longest_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self._clips if not clip.is_recording]
        if len(clips) == 0:
            return None
        else:
            return max(clips, key=lambda c: c.length)

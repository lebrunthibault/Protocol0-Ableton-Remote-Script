from typing import Optional, Callable

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.shared.SongFacade import SongFacade


class ScenePlayingPosition(object):
    def __init__(self, clips, scene_length, scrub_by):
        # type: (SceneClips, SceneLength, Callable) -> None
        self._clips = clips
        self._scene_length = scene_length
        self._scrub_by = scrub_by

    def __repr__(self):
        # type: () -> str
        return "position: %s, bar_position: %s, current_bar: %s, in_last_bar: %s" % (
            self.position, self.bar_position, self.current_bar, self.in_last_bar
        )

    @property
    def position(self):
        # type: () -> float
        if self._longest_un_muted_clip:
            return self._longest_un_muted_clip.playing_position.position
        else:
            return 0

    @property
    def bar_position(self):
        # type: () -> float
        return self.position / SongFacade.signature_numerator()

    @property
    def current_bar(self):
        # type: () -> int
        if self._scene_length.length == 0:
            return 0
        return int(self.bar_position)

    @property
    def in_last_bar(self):
        # type: () -> bool
        return self.current_bar == self._scene_length.bar_length - 1

    @property
    def _longest_un_muted_clip(self):
        # type: () -> Optional[Clip]
        clips = [clip for clip in self._clips if not clip.is_recording and not clip.muted]
        if len(clips) == 0:
            return None
        else:
            return max(clips, key=lambda c: c.length)

    def jump_to_bar(self, bar_position):
        # type: (float) -> None
        beat_offset = (bar_position * SongFacade.signature_numerator()) - self.position
        self._scrub_by(beat_offset - 0.5)

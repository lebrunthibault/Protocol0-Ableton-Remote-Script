from functools import partial

import Live
from typing import TYPE_CHECKING, Any

from protocol0.lom.clip.Clip import Clip
from protocol0.utils.decorators import p0_subject_slot, defer

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleAudioTrack
        self._warping_listener.subject = self._clip

    @p0_subject_slot("warping")
    @defer
    def _warping_listener(self):
        # type: () -> None
        """ neither dummy clip on """
        if not self.warping and self.track.CLIP_WARPING_MANDATORY:
            self.warping = True
        if self.warping:
            self.looping = True

    @property
    def warping(self):
        # type: () -> float
        return self._clip.warping if self._clip else 0

    @warping.setter
    def warping(self, warping):
        # type: (float) -> None
        if self._clip:
            self._clip.warping = warping

    @property
    def warp_mode(self):
        # type: () -> Live.Clip.WarpMode
        return self._clip.warp_mode

    @warp_mode.setter
    def warp_mode(self, warp_mode):
        # type: (Live.Clip.WarpMode) -> None
        if self._clip:
            self._clip.warp_mode = warp_mode

    @p0_subject_slot("looping")
    def _looping_listener(self):
        # type: () -> None
        if self.warping:
            # enforce looping
            self.parent.defer(partial(setattr, self._clip, "looping", True))

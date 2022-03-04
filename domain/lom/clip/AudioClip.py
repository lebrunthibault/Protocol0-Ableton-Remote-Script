from functools import partial

from typing import TYPE_CHECKING

import Live
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.Colorer import Colorer
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
    from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot


# noinspection PyPropertyAccess
class AudioClip(Clip):
    def __init__(self, clip_slot):
        # type: (AudioClipSlot) -> None
        super(AudioClip, self).__init__(clip_slot)
        self.track = self.track  # type: SimpleAudioTrack
        self.clip_slot = self.clip_slot  # type: AudioClipSlot
        self._warping_listener.subject = self._clip

    @p0_subject_slot("warping")
    def _warping_listener(self):
        # type: () -> None
        if self.warping:
            Scheduler.defer(partial(setattr, self, "looping", True))
        # noinspection PyUnresolvedReferences
        self.notify_length()

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
        return self._clip.warp_mode if self._clip else Live.Clip.WarpMode.beats

    @warp_mode.setter
    def warp_mode(self, warp_mode):
        # type: (Live.Clip.WarpMode) -> None
        if self._clip:
            self._clip.warp_mode = warp_mode

    @property
    def file_path(self):
        # type: () -> str
        return self._clip.file_path if self._clip else ""

    def crop(self):
        # type: () -> None
        """ Live.Clip.Clip.crop_sample doesn't exists so we notify the user """
        if self.loop.start != 0:
            Colorer.blink(self)
            Backend.client().show_warning("Please crop %s" % self)

from functools import partial

from typing import TYPE_CHECKING, cast

import Live
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.ColorEnum import ColorEnum
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot  # noqa


class AudioClip(Clip):
    def __init__(self, clip_slot):
        # type: (AudioClipSlot) -> None
        super(AudioClip, self).__init__(clip_slot)
        from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
        from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot  # noqa

        self.track = cast(SimpleAudioTrack, self.track)
        self.clip_slot = cast(AudioClipSlot, self.clip_slot)
        self._warping_listener.subject = self._clip
        Scheduler.defer(self.refresh_appearance)

    @property
    def warping(self):
        # type: () -> float
        return self._clip.warping if self._clip else 0

    @warping.setter
    def warping(self, warping):
        # type: (float) -> None
        if self._clip:
            self._clip.warping = warping

    @p0_subject_slot("warping")
    def _warping_listener(self):
        # type: () -> None
        if self.warping:
            Scheduler.defer(partial(setattr, self, "looping", True))
        # noinspection PyUnresolvedReferences
        self.notify_length()

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
        """ Live.Clip.Clip.crop_sample doesn't exist so we notify the user """
        if self.loop.start != 0:
            self.color = ColorEnum.WARNING.color_int_value
            Scheduler.defer(self.select)
            Logger.warning("Please crop %s" % self)

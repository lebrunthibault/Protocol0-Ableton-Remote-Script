import Live
from typing import Any

from protocol0.domain.lom.clip.AudioClipCreatedEvent import AudioClipCreatedEvent
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.shared.logging.Logger import Logger


class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        Scheduler.defer(self.appearance.refresh)
        DomainEventBus.emit(AudioClipCreatedEvent())

    @property
    def warp_mode(self):
        # type: () -> Live.Clip.WarpMode
        return self._clip.warp_mode

    @warp_mode.setter
    def warp_mode(self, warp_mode):
        # type: (Live.Clip.WarpMode) -> None
        self._clip.warp_mode = warp_mode

    @property
    def file_path(self):
        # type: () -> str
        return self._clip.file_path if self._clip else ""

    def crop(self):
        # type: () -> None
        """Live.Clip.Clip.crop_sample doesn't exist, so we notify the user"""
        self.loop.fix()
        self.appearance.color = ColorEnum.WARNING.color_int_value
        Logger.warning("Please crop %s" % self)

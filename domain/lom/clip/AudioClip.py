from functools import partial

from _Framework.SubjectSlot import subject_slot
from typing import Any

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.shared.logging.Logger import Logger


class AudioClip(Clip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClip, self).__init__(*a, **k)
        self._warping_listener.subject = self._clip
        Scheduler.defer(self.appearance.refresh)

    @subject_slot("warping")
    def _warping_listener(self):
        # type: () -> None
        if self._clip.warping:
            Scheduler.defer(partial(setattr, self, "looping", True))
        self.notify_observers()

    @property
    def file_path(self):
        # type: () -> str
        return self._clip.file_path if self._clip else ""

    def crop(self):
        # type: () -> None
        """ Live.Clip.Clip.crop_sample doesn't exist so we notify the user """
        if self.loop.start != 0:
            self.appearance.color = ColorEnum.WARNING.color_int_value
            Logger.warning("Please crop %s" % self)

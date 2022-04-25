import re
from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from _Framework.SubjectSlot import subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import get_length_legend
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipName(UseFrameworkEvents):
    DEBUG = False

    def __init__(self, clip):
        # type: (Clip) -> None
        super(ClipName, self).__init__()
        self.clip = clip
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True),
                           "loop_start")  # type: ignore[arg-type]
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True),
                           "loop_end")  # type: ignore[arg-type]
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True),
                           "start_marker")  # type: ignore[arg-type]
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True),
                           "end_marker")  # type: ignore[arg-type]
        self._name_listener.subject = self.clip._clip
        self._base_name = None  # type: Optional[str]

    @property
    def base_name(self):
        # type: () -> str
        """ lazy loading """
        if self._base_name is None:
            self._base_name = self._get_base_name()
        return self._base_name

    @base_name.setter
    def base_name(self, base_name):
        # type: (str) -> None
        self._base_name = base_name

    @subject_slot("name")
    def _name_listener(self, force=False):
        # type: (bool) -> None
        base_name = self._get_base_name()
        if not force and base_name == self.base_name and self.clip.name != base_name:
            return
        self.base_name = base_name
        self.normalize_base_name()
        Scheduler.defer(self.update)

    def _get_base_name(self):
        # type: () -> str
        clip_name = self.clip.name or ""
        if re.match("^\\d+\\s(bar|beat)s?", clip_name):
            return ""
        match = re.match("^(?P<base_name>[^(]*)", clip_name)

        return match.group("base_name").strip() if match else ""

    def normalize_base_name(self):
        # type: () -> None
        if re.match("^%s( \\d+)?" % self.clip.track.name, self.base_name) is not None:
            self.base_name = ""

    @property
    def _length_legend(self):
        # type: () -> str
        if hasattr(self.clip, "warping") and not self.clip.warping:
            return "unwarped"

        return get_length_legend(beat_length=self.clip.length)

    def update(self, base_name=None):
        # type: (Optional[str]) -> None
        if self.clip.is_recording:
            return None
        if self.DEBUG:
            Logger.info("%s : %s <-> %s <-> %s" % (self.clip, base_name, self.base_name, self.clip.name))
        if base_name is not None:
            self.base_name = base_name
        if self.base_name:
            clip_name = "%s (%s)" % (self.base_name, self._length_legend)
        else:
            clip_name = self._length_legend
        self.clip.name = clip_name

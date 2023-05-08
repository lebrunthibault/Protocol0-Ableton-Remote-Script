import re
from functools import partial

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional

from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.string import smart_string
from protocol0.domain.shared.utils.utils import get_length_legend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ClipName(SlotManager):
    _DEBUG = False

    def __init__(self, live_clip):
        # type: (Live.Clip.Clip) -> None
        super(ClipName, self).__init__()
        self._live_clip = live_clip
        self.register_slot(self._live_clip, partial(self._name_listener, force=True), "loop_start")
        self.register_slot(self._live_clip, partial(self._name_listener, force=True), "loop_end")
        self.register_slot(
            self._live_clip, partial(self._name_listener, force=True), "start_marker"
        )
        self.register_slot(self._live_clip, partial(self._name_listener, force=True), "end_marker")
        self._name_listener.subject = self._live_clip
        self._base_name = None  # type: Optional[str]

    @property
    def name(self):
        # type: () -> str
        if self._live_clip:
            return smart_string(self._live_clip.name)
        else:
            return ""

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._live_clip and name:
            self._live_clip.name = str(name).strip()  # noqa

    @property
    def base_name(self):
        # type: () -> str
        """lazy loading"""
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
        # base_name != "" is for renaming empty clips
        if (
            not force
            and base_name == self.base_name
            and base_name != ""
            and self._live_clip.name != base_name
        ):
            return
        self.base_name = base_name
        Scheduler.defer(self.update)

    def _get_base_name(self):
        # type: () -> str
        # noinspection PyBroadException
        try:
            clip_name = self._live_clip.name or ""
        except Exception:
            return ""

        if re.match("^\\d+\\s?(bar|beat|b)?s?\\s*$", clip_name):
            return ""
        match = re.match("^(?P<base_name>[^(]*)", clip_name)

        base_name = match.group("base_name").strip() if match else ""

        if base_name.isdigit():
            return ""
        else:
            return base_name

    def _get_length_legend(self):
        # type: () -> str
        try:
            if hasattr(self._live_clip, "warping") and not self._live_clip.warping:
                return ""
        except RuntimeError:
            pass

        return get_length_legend(
            self._live_clip.loop_end - self._live_clip.loop_start,
            Song.signature_numerator(),
        )

    def update(self, base_name=None):
        # type: (Optional[str]) -> None
        if not self._live_clip:
            return None
        if self._live_clip.is_recording:
            return None
        if self._DEBUG:
            Logger.info("%s <-> %s <-> %s" % (base_name, self.base_name, self._live_clip.name))

        if base_name is not None:
            self.base_name = base_name

        length_legend = self._get_length_legend()

        if self.base_name:
            if length_legend:
                clip_name = "%s (%s)" % (self.base_name, length_legend)
            else:
                clip_name = self.base_name
        else:
            clip_name = self._get_length_legend()

        self._live_clip.name = clip_name

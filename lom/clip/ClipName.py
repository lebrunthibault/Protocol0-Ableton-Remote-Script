import re
from functools import partial

from typing import TYPE_CHECKING, Any, Optional

from protocol0.lom.AbstractObjectName import AbstractObjectName

if TYPE_CHECKING:
    from protocol0.lom.clip.Clip import Clip


class ClipName(AbstractObjectName):
    DEBUG = False

    def __init__(self, clip, *a, **k):
        # type: (Clip, Any, Any) -> None
        super(ClipName, self).__init__(clip, *a, **k)
        self.clip = clip
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True), "loop_start")
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True), "loop_end")
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True), "start_marker")
        self.register_slot(self.clip._clip, partial(self._name_listener, force=True), "end_marker")
        self._name_listener.subject = self.clip._clip

    def _get_base_name(self):
        # type: () -> str
        clip_name = self.clip.name or ""
        if re.match("^\\d+\\s(bar|beat)s?", clip_name):
            return ""
        match = re.match("^(?P<base_name>[^(]*)", clip_name)

        return match.group("base_name").strip() if match else ""

    def normalize_base_name(self):
        # type: () -> None
        track_base_name = self.clip.track.base_name.strip()
        if track_base_name and re.match("^%s( \\d+)?" % track_base_name, self.base_name) is not None:
            self.base_name = ""

    @property
    def _length_legend(self):
        # type: () -> str
        if hasattr(self.clip, "warping") and not self.clip.warping:
            return "unwarped"

        return self.parent.utilsManager.get_length_legend(length=self.clip.length)

    def update(self, base_name=None):
        # type: (Optional[str]) -> None
        if self.clip.is_recording:
            return None
        if self.DEBUG:
            self.parent.log_info("%s : %s <-> %s <-> %s" % (self.clip, base_name, self.base_name, self.clip.name))
        if base_name is not None:
            self.base_name = base_name
        if self.base_name:
            clip_name = "%s (%s)" % (self.base_name, self._length_legend)
        else:
            clip_name = self._length_legend
        self.clip.name = clip_name

import re

from typing import TYPE_CHECKING, Any, Optional

from protocol0.lom.AbstractObjectName import AbstractObjectName
from protocol0.utils.decorators import defer

if TYPE_CHECKING:
    from protocol0.lom.clip.Clip import Clip


class ClipName(AbstractObjectName):
    def __init__(self, clip, *a, **k):
        # type: (Clip, Any, Any) -> None
        super(ClipName, self).__init__(clip, *a, **k)
        self.clip = clip
        self.register_slot(self.clip._clip, self.update, "loop_start")
        self.register_slot(self.clip._clip, self.update, "loop_end")
        self.register_slot(self.clip._clip, self.update, "start_marker")
        self.register_slot(self.clip._clip, self.update, "end_marker")
        self._name_listener.subject = self.clip._clip

    def _get_base_name(self):
        # type: () -> str
        match = re.match("^(?P<base_name>[^().]*).*$", self.clip.name or "")
        return match.group("base_name").strip() if match else ""

    def normalize_base_name(self):
        # type: () -> None
        super(ClipName, self).normalize_base_name()
        track_base_name = self.clip.track.base_name.strip()
        if track_base_name and re.match("^%s( \\d+)?" % track_base_name, self.base_name):
            self.base_name = ""

    @property
    def _length_legend(self):
        # type: () -> str
        if hasattr(self.clip, "warping") and not self.clip.warping:
            return "unwarped"

        if int(self.clip.length) % self.song.signature_numerator != 0:
            return "%d beat%s" % (self.clip.length, "s" if self.clip.length > 1 else "")
        else:
            return "%d bar%s" % (self.clip.bar_length, "s" if self.clip.bar_length > 1 else "")

    @defer
    def update(self, base_name=None):
        # type: (Optional[str]) -> None
        """ extended """
        if self.clip.is_recording:
            return None
        self.base_name = base_name if base_name is not None else self.base_name
        clip_name = "%s (%s)" % (self.base_name, self._length_legend)
        if not self.clip.is_dummy and self.clip.tail_bar_length:
            clip_name += " tail"
        # self.parent.log_dev("%s <-> %s <-> %s" % (self.clip, self.clip.name, clip_name))
        self.clip.name = clip_name

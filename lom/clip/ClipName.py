import re

from typing import TYPE_CHECKING, Any, Optional

from a_protocol_0.config import Config
from a_protocol_0.lom.AbstractObjectName import AbstractObjectName
from a_protocol_0.utils.decorators import p0_subject_slot, defer

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.Clip import Clip


class ClipName(AbstractObjectName):
    def __init__(self, clip, *a, **k):
        # type: (Clip, Any, Any) -> None
        super(ClipName, self).__init__(*a, **k)
        self.clip = clip
        self.clips = [self.clip]
        self.base_name = ""
        self.register_slot(self.clip._clip, self.update, "loop_start")
        self.register_slot(self.clip._clip, self.update, "loop_end")
        self.register_slot(self.clip._clip, self.update, "start_marker")
        self.register_slot(self.clip._clip, self.update, "end_marker")
        self._name_listener.subject = clip._clip
        self.prev_name = ""
        self.parent.defer(self._name_listener)  # type: ignore[arg-type]

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        """ overridden """
        match = re.match("^(\d+ bars?\s?)?(?P<base_name>[^()[\].]*).*$", self.clip.name or "")
        self.base_name = match.group("base_name").strip() if match else ""
        if Config.FIX_OUTDATED_SETS:
            self.normalize_base_name()
        self.update()

    def normalize_base_name(self):
        # type: () -> None
        super(ClipName, self).normalize_base_name()
        if re.match("^%s( \d+)?" % self.clip.track.base_name.strip(), self.base_name):
            self.base_name = ""

    @property
    def length_legend(self):
        # type: () -> str
        if hasattr(self.clip, "warping") and not self.clip.warping:
            return "unwarped"

        if int(self.clip.length) % self.song.signature_denominator != 0:
            return "%d beat%s" % (self.clip.length, "s" if self.clip.length > 1 else "")
        else:
            bar_count = self.clip.length / self.song.signature_denominator
            return "%d bar%s" % (bar_count, "s" if bar_count > 1 else "")

    @defer
    def update(self, base_name=None):
        # type: (Optional[str]) -> None
        """ extended """
        if self.clip.is_recording:
            return None
        self.base_name = base_name if base_name is not None else self.base_name
        self.clip.name = "%s (%s)" % (self.base_name, self.length_legend)
        self.prev_name = self.clip.name

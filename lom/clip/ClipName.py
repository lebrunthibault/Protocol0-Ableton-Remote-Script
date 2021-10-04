import re

from typing import TYPE_CHECKING, Any, Optional

from protocol0.lom.AbstractObjectName import AbstractObjectName
from protocol0.utils.decorators import p0_subject_slot, defer

if TYPE_CHECKING:
    from protocol0.lom.clip.Clip import Clip


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
        self.parent.defer(self._name_listener)  # type: ignore[arg-type]

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        """ overridden """
        match = re.match("^(?P<base_name>[^()[\\].]*).*$", self.clip.name or "")
        self.base_name = match.group("base_name").strip() if match else ""
        self.normalize_base_name()
        self.update()

    @property
    def is_valid(self):
        # type: () -> bool
        """ identifies whether this clip name has been generated by protocol0 """
        return "_" not in self.clip.name and \
               any([duration_keyword in self.clip.name for duration_keyword in ("bar", "beat")])

    def normalize_base_name(self):
        # type: () -> None
        super(ClipName, self).normalize_base_name()
        if re.match("^%s( \\d+)?" % self.clip.track.base_name.strip(), self.base_name):
            self.base_name = ""

    @property
    def length_legend(self):
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
        self.clip.name = "%s (%s)" % (self.base_name, self.length_legend)

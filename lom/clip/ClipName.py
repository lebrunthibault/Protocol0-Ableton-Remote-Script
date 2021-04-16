import re

from typing import TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import p0_subject_slot, defer

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.Clip import Clip


class ClipName(AbstractObject):
    def __init__(self, clip, *a, **k):
        # type: (Clip) -> None
        super(ClipName, self).__init__(*a, **k)
        self.clip = clip
        self.base_name = ""
        self.is_playable = False
        self.register_slot(self.clip._clip, self.update, "loop_start")
        self.register_slot(self.clip._clip, self.update, "loop_end")
        self.register_slot(self.clip._clip, self.update, "start_marker")
        self.register_slot(self.clip._clip, self.update, "end_marker")
        self._name_listener.subject = clip._clip
        self.prev_name = ""
        self.parent.defer(self._name_listener)

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        """ overridden """
        match = re.match("^(?P<base_name>[^().]*)(\(.*\))?(?P<is_playable>\.)?.*$", self.clip.name or "")
        self.base_name = match.group("base_name").strip() if match else ""
        if self.base_name.strip() == self.clip.track.base_name.strip():
            self.base_name = ""
        self.is_playable = bool(match.group("is_playable")) if match else False
        self.update()

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
    def update(self, base_name=None, is_playable=None):
        # type: (str, bool) -> None
        """ extended """
        if self.clip.is_recording:
            return
        self.is_playable = is_playable if is_playable is not None else self.is_playable
        self.base_name = base_name if base_name is not None else self.base_name
        name = self.base_name + " " if self.base_name else ""
        self.clip.name = "%s(%s)%s" % (name, self.length_legend, "." if self.is_playable else "")
        self.prev_name = self.clip.name

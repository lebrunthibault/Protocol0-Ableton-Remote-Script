import re

from typing import TYPE_CHECKING

from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.clip.Clip import Clip


class ClipName(AbstractObject):
    def __init__(self, clip, *a, **k):
        # type: (Clip) -> None
        super(ClipName, self).__init__(clip, *a, **k)
        self.clip = clip
        self.base_name = ""
        self.is_playable = False
        self.register_slot(self.clip._clip, self.set_clip_name, "loop_start")
        self.register_slot(self.clip._clip, self.set_clip_name, "loop_end")
        self.register_slot(self.clip._clip, self.set_clip_name, "start_marker")
        self.register_slot(self.clip._clip, self.set_clip_name, "end_marker")
        self._name_listener.subject = clip._clip
        self.prev_name = ""
        self.parent.defer(self._name_listener)

    def __repr__(self):
        return "ClipName of %s" % self.clip

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        """ overridden """
        match = re.match("^(?P<base_name>[^()]*)(\(.*\))(?P<is_playable>\.)?.*$", self.clip.name)
        self.base_name = match.group("base_name").strip() if match else ""
        self.is_playable = bool(match.group("is_playable")) if match else False
        self.set_clip_name()

    @property
    def length_legend(self):
        # type: () -> str
        if int(self.clip.length) % 4 != 0:
            return "%d beat%s" % (self.clip.length, "s" if self.clip.length > 1 else "")
        else:
            bar_count = self.clip.length / 4
            return "%d bar%s" % (bar_count, "s" if bar_count > 1 else "")

    def set_clip_name(self, base_name=None, is_playable=None):
        # type: (str, bool) -> None
        """ extended """
        if self.clip.is_recording:
            return
        self.is_playable = is_playable if is_playable is not None else self.is_playable
        name = base_name or self.base_name
        name += " " if name else ""
        self.prev_name = self.clip.name = "%s(%s)%s" % (name, self.length_legend, "." if self.is_playable else "")

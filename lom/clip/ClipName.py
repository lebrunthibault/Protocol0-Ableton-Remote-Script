import Live
from typing import TYPE_CHECKING, List

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
        self._name_listener.subject = clip._clip
        self._name_listener()
        self.register_slot(self.clip._clip, self.set, "loop_start")
        self.register_slot(self.clip._clip, self.set, "loop_end")
        self.register_slot(self.clip._clip, self.set, "start_marker")
        self.register_slot(self.clip._clip, self.set, "end_marker")

    def __repr__(self):
        return "ClipName of %s" % self.clip

    @property
    def bar_count(self):
        # type: () -> int
        return int(round(self.clip.length / 4))

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        parts = self.clip.name.split(" - ")
        self.base_name = parts[0]

    def set(self, base_name=None):
        # type: (str) -> None
        if self.clip.is_recording:
            return
        self.base_name = base_name or self.base_name
        name = "%s - %d bar" % (self.base_name, self.bar_count)
        if self.bar_count > 1:
            name += "s"
        self.clip.name = name

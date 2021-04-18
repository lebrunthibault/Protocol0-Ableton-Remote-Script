import Live
from typing import TYPE_CHECKING

from _Framework.ControlSurface import get_control_surfaces
from _Framework.SubjectSlot import SlotManager, Subject
from _Framework.Util import find_if

if TYPE_CHECKING:
    from a_protocol_0.lom.Song import Song
    from a_protocol_0 import Protocol0  # noqa


class AbstractObject(SlotManager, Subject):
    def __init__(self, *a, **k):
        super(AbstractObject, self).__init__(*a, **k)
        from a_protocol_0 import Protocol0

        self._parent = find_if(lambda cs: isinstance(cs, Protocol0), get_control_surfaces())

    def __repr__(self):
        repr = "P0 %s" % self.__class__.__name__
        if hasattr(self, "name") and isinstance(self.name, str):
            repr = "%s: %s" % (repr, self.name)
        if hasattr(self, "index") and isinstance(self.index, str):
            repr = "%s (%s)" % (repr, self.index)
        if hasattr(self, "_device") and isinstance(self._device, Live.Device.Device):
            repr = "%s (dev %s)" % (repr, self._device)

        return repr

    def __hash__(self):
        return hash(repr(self))

    def __ne__(self, obj):
        # type: (object) -> bool
        return not obj or not self == obj

    @property
    def parent(self):
        # type: () -> Protocol0
        """ to get a working type hint """
        return self._parent

    @property
    def song(self):
        # type: () -> Song
        return self.parent.protocol0_song

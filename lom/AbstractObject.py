from p0_system_api import DefaultApi
from typing import TYPE_CHECKING, Any

from _Framework.ControlSurface import get_control_surfaces
from _Framework.SubjectSlot import SlotManager, Subject
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.Song import Song
    from protocol0.Protocol0 import Protocol0


class AbstractObject(SlotManager, Subject):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AbstractObject, self).__init__(*a, **k)
        from protocol0 import Protocol0

        parent = find_if(lambda cs: isinstance(cs, Protocol0), get_control_surfaces())
        assert parent
        self._parent = parent  # type: Protocol0

    def __repr__(self):
        # type: () -> str
        out = "P0 %s" % self.__class__.__name__
        if hasattr(self, "base_name") and self.base_name:
            out += ": %s" % self.base_name
        elif hasattr(self, "name"):
            out += ": %s" % self.name

        return out

    def __ne__(self, obj):
        # type: (object) -> bool
        return not obj or not self == obj

    @property
    def system(self):
        # type: () -> DefaultApi
        """
        Access to non restricted (system) python environment over MIDI
        """
        return self._parent.p0_system_api_client

    @property
    def parent(self):
        # type: () -> Protocol0
        """ to get a working type hint """
        return self._parent

    @property
    def song(self):
        # type: () -> Song
        return self.parent.protocol0_song

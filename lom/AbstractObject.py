from openapi_client import DefaultApi
from traitlets import Any
from typing import TYPE_CHECKING

from _Framework.ControlSurface import get_control_surfaces
from _Framework.SubjectSlot import SlotManager, Subject
from a_protocol_0.utils.utils import find_if

if TYPE_CHECKING:
    from a_protocol_0.lom.Song import Song
    from a_protocol_0.Protocol0 import Protocol0


class AbstractObject(SlotManager, Subject):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AbstractObject, self).__init__(*a, **k)
        from a_protocol_0 import Protocol0

        parent = find_if(lambda cs: isinstance(cs, Protocol0), get_control_surfaces())
        assert parent
        self._parent = parent  # type: Protocol0

    def __repr__(self):
        # type: () -> str
        repr = "P0 %s" % self.__class__.__name__
        if hasattr(self, "base_name") and self.base_name:
            repr += ": %s" % self.base_name
        elif hasattr(self, "name"):
            repr += ": %s" % self.name

        return repr

    def __ne__(self, obj):
        # type: (object) -> bool
        return not obj or not self == obj

    @property
    def system(self):
        # type: () -> DefaultApi
        """ non restricted python scripts access via local API """
        return self._parent.api_client

    @property
    def parent(self):
        # type: () -> Protocol0
        """ to get a working type hint """
        return self._parent

    @property
    def song(self):
        # type: () -> Song
        return self.parent.protocol0_song

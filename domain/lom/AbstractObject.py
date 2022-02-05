from _Framework.SubjectSlot import SlotManager, Subject
from protocol0.shared.AccessGlobalState import AccessGlobalState


class AbstractObject(AccessGlobalState, SlotManager, Subject):
    """
        Base class for domain entities
        Providing global access to services (should be changed)
        as well as extending appropriate classes to use ableton event system
    """

    def __repr__(self):
        # type: () -> str
        out = "P0 %s" % self.__class__.__name__
        if hasattr(self, "base_name") and self.base_name:
            out += ": %s" % self.base_name
        elif hasattr(self, "name"):
            out += ": %s" % self.name
        if hasattr(self, "index"):
            out += " (%s)" % self.index

        return out

    def __ne__(self, obj):
        # type: (object) -> bool
        return not obj or not self == obj

    def to_json(self):
        # type: () -> str
        return str(self)

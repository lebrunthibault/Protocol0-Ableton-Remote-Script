from typing_extensions import Protocol
from typing import Any


def liveobj_valid(obj):
    # type: (Any) -> bool
    u"""
    Check whether obj represents a valid Live API obj.

    This will return False both if obj represents a lost weakref or is None.
    It's important that Live API objects are not checked using "is None", since this
    would treat lost weakrefs as valid.
    """
    return obj != None  # noqa


class LiveObject(Protocol):
    @property
    def _live_ptr(self):
        # type: () -> int
        raise NotImplementedError

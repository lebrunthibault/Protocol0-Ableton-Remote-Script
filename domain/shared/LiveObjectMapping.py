import collections

from typing import Dict, Any, Callable, List

from protocol0.domain.shared.LiveObject import LiveObject
from protocol0.shared.types import T


class LiveObjectMapping(object):
    def __init__(self, factory):
        # type: (Callable[..., T]) -> None
        self._live_id_to_object = collections.OrderedDict()  # type: Dict[int, Any]
        self._objects = []  # type: List[Any]
        self._factory = factory
        self._removed_objects = []  # type: List[Any]
        self._added_objects = []  # type: List[Any]

    def __repr__(self):
        # type: () -> str
        return "all: %s, added: %s, removed: %s" % (self.all, self.added, self.removed)

    @property
    def all(self):
        # type: () -> List[T]
        return self._objects

    @property
    def added(self):
        # type: () -> List[T]
        return self._added_objects

    @property
    def removed(self):
        # type: () -> List[T]
        return self._removed_objects

    def build(self, live_objects):
        # type: (List[LiveObject]) -> None
        live_id_to_object = collections.OrderedDict()  # type: Dict[int, Any]
        for live_object in live_objects:
            live_id_to_object[live_object._live_ptr] = self._create_object(live_object)

        self._added_objects = list(
            set(live_id_to_object.values()) - set(self._live_id_to_object.values())
        )
        self._removed_objects = list(
            set(self._live_id_to_object.values()) - set(live_id_to_object.values())
        )

        self._live_id_to_object = live_id_to_object
        self._objects = list(self._live_id_to_object.values())

    def _create_object(self, live_object):
        # type: (LiveObject) -> T
        if live_object._live_ptr in self._live_id_to_object:
            return self._live_id_to_object[live_object._live_ptr]
        else:
            return self._factory(live_object)

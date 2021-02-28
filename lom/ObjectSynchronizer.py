from functools import partial

from typing import List, Set

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject


class ObjectSynchronizer(AbstractControlSurfaceComponent):
    """ Class that handles the parameter sync of 2 objects (usually track or clip) """
    def __init__(self, master, slave, subject_name, properties, bidirectional=True, *a, **k):
        # type: (AbstractObject, AbstractObject, str, List[str]) -> None
        super(ObjectSynchronizer, self).__init__(*a, **k)

        if not master or not slave:
            raise Protocol0Error("Master and slave should be objects")
        # sync is two way but the master clip defines start values
        self.properties = properties
        self.updating_properties = set()  # type: Set[str]

        for property in self.properties:
            self.register_slot(getattr(master, subject_name), partial(self._sync_properties, master, slave), property)
            if bidirectional:
                self.register_slot(getattr(slave, subject_name), partial(self._sync_properties, slave, master), property)

        self._sync_properties(master, slave)

    def _sync_properties(self, master, slave):
        for property in self.properties:
            if property in self.updating_properties:  # handle update loop
                return
            value = getattr(master, property)
            if value is not None and getattr(slave, property) != value:
                self.updating_properties.add(property)
                self.parent.defer(partial(self.updating_properties.discard, property))
                self.parent.defer(partial(setattr, slave, property, value))


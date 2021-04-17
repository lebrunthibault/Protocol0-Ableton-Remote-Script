from functools import partial

from typing import List, Set, Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject


class ObjectSynchronizer(AbstractControlSurfaceComponent):
    """
    Class that handles the parameter sync of 2 objects (usually track or clip)
    listenable_properties are properties that trigger the sync
    properties are properties effectively synced
    """

    def __init__(self, master, slave, subject_name, listenable_properties=None, properties=[], *a, **k):
        # type: (AbstractObject, AbstractObject, str, Optional[List[str]], List[str]) -> None
        super(ObjectSynchronizer, self).__init__(*a, **k)

        if not master or not slave:
            raise Protocol0Error("Master and slave should be objects")

        self.master = master
        self.slave = slave

        self.listenable_properties = listenable_properties or properties
        # sync is two way but the master clip defines start values
        self.properties = properties
        self.updating_properties = set()  # type: Set[str]

        for property in self.listenable_properties:
            self.register_slot(getattr(master, subject_name), partial(self._sync_properties, master, slave), property)
            self.register_slot(getattr(slave, subject_name), partial(self._sync_properties, slave, master), property)

        self._sync_properties(master, slave)

    def get_syncable_properties(self, changed_object):
        # type: (AbstractObject) -> List[str]
        """ getter allows dynamic syncing configurable in child classes """
        return self.properties

    def _sync_properties(self, master, slave):
        # type: (AbstractObject, AbstractObject) -> None
        for property in self.get_syncable_properties(master):
            if property in self.updating_properties:  # handle update loop
                return
            self.sync_property(master, slave, property)

    def sync_property(self, master, slave, property):
        # type: (AbstractObject, AbstractObject, str) -> None
        value = getattr(master, property)
        if value is not None and getattr(slave, property) != value:
            self.updating_properties.add(property)
            self.parent.defer(partial(self.updating_properties.discard, property))
            self.parent.defer(partial(setattr, slave, property, value))

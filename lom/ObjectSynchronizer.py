from functools import partial

from typing import List, Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.utils.decorators import defer


class ObjectSynchronizer(AbstractControlSurfaceComponent):
    """
    Class that handles the parameter sync of 2 objects (usually track or clip)
    listenable_properties are properties that trigger the sync
    properties are properties effectively synced
    """

    def __init__(self, master, slave, subject_name, listenable_properties=None, properties=[], *a, **k):
        # type: (AbstractObject, AbstractObject, str, Optional[List[str]], List[str], Any, Any) -> None
        super(ObjectSynchronizer, self).__init__(*a, **k)

        if not master or not slave:
            raise Protocol0Error("Master and slave should be objects")

        self.master = master
        self.slave = slave

        self.listenable_properties = listenable_properties or properties
        # sync is two way but the master clip defines start values
        self.properties = properties

        for property in self.listenable_properties:
            self.register_slot(getattr(master, subject_name), partial(self._sync_properties, master, slave), property)
            self.register_slot(getattr(slave, subject_name), partial(self._sync_properties, slave, master), property)

        self._sync_properties(master, slave)

    def get_syncable_properties(self, _):
        # type: (AbstractObject) -> List[str]
        """ getter allows dynamic syncing configurable in child classes """
        return self.properties

    @defer
    def _sync_properties(self, master, slave):
        # type: (AbstractObject, AbstractObject) -> None
        for property in self.get_syncable_properties(master):
            self.sync_property(master, slave, property)

    def sync_property(self, master, slave, property):
        # type: (AbstractObject, AbstractObject, str) -> None
        master_value = getattr(master, property)
        slave_value = getattr(slave, property)
        if master_value is not None and slave_value != master_value:
            setattr(slave, property, master_value)

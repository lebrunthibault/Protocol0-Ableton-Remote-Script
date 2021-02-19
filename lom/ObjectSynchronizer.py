from functools import partial

from typing import List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.utils.decorators import defer


class ObjectSynchronizer(AbstractControlSurfaceComponent):
    """ Class that handles the parameter sync of 2 clips """
    def __init__(self, master, slave, subject_name, properties, *a, **k):
        # type: (AbstractObject, AbstractObject, str, List[str]) -> None
        super(ObjectSynchronizer, self).__init__(*a, **k)
        # sync is two way but the master clip defines start values
        self.properties = properties
        self.master = master
        self.slave = slave

        for property in self.properties:
            self.register_slot(getattr(master, subject_name), self._sync_slave_properties, property)
            self.register_slot(getattr(slave, subject_name), self._sync_master_properties, property)

        self._sync_slave_properties()

    def _sync_slave_properties(self):
        for property in self.properties:
            value = getattr(self.master, property)
            if value is not None and getattr(self.slave, property) != value:
                self.parent.defer(partial(setattr, self.slave, property, value))

    @defer
    def _sync_master_properties(self):
        for property in self.properties:
            value = getattr(self.slave, property)
            if value is not None and getattr(self.master, property) != value:
                self.parent.defer(partial(setattr, self.master, property, value))



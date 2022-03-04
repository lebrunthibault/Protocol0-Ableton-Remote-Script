from functools import partial

from typing import List

from protocol0.domain.lom.SynchronizableObjectInterface import SynchronizableObjectInterface
from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class ObjectSynchronizer(UseFrameworkEvents):
    """ Class that handles the parameter sync of 2 linked objects """

    def __init__(self, master, slave, listenable_properties):
        # type: (SynchronizableObjectInterface, SynchronizableObjectInterface, List[str]) -> None
        super(ObjectSynchronizer, self).__init__()

        if not isinstance(master, SynchronizableObjectInterface) or not isinstance(slave,
                                                                                   SynchronizableObjectInterface):
            raise Protocol0Error("Master and slave should be SynchronizableObjectInterface")

        lom_property_name = master.lom_property_name

        for property_name in listenable_properties:
            self.register_slot(getattr(master, lom_property_name),
                               partial(Scheduler.defer, partial(self._sync_property, master, slave, property_name)),
                               property_name)

    def _sync_property(self, master, slave, property_name):
        # type: (SynchronizableObjectInterface, SynchronizableObjectInterface, str) -> None
        if not slave.is_syncable:
            return

        master_value = getattr(master, property_name)
        slave_value = getattr(slave, property_name)

        if slave_value != master_value:
            setattr(slave, property_name, master_value)

from functools import partial

from typing import List, Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject


class ObjectSynchronizer(AbstractControlSurfaceComponent):
    """
    Class that handles the parameter sync of 2 objects (usually track or clip)
    listenable_properties are properties that trigger the sync
    properties are properties effectively synced
    """

    def __init__(self, master, slave, listenable_properties=None, bidirectional=True, *a, **k):
        # type: (AbstractObject, AbstractObject, Optional[List[str]], bool, Any, Any) -> None
        super(ObjectSynchronizer, self).__init__(*a, **k)

        if not master or not slave:
            raise Protocol0Error("Master and slave should be objects")

        lom_property_name = self._get_lom_property_name_from_object(obj=master)

        # sync is two way but the master object defines start values
        self.listenable_properties = listenable_properties or []

        for property_name in self.listenable_properties:
            self.register_slot(getattr(master, lom_property_name),
                               partial(self.parent.defer, partial(self._sync_property, master, slave, property_name)),
                               property_name)
            if bidirectional:
                self.register_slot(getattr(slave, lom_property_name),
                                   partial(self.parent.defer, partial(self._sync_property, slave, master, property_name)),
                                   property_name)

    def _get_lom_property_name_from_object(self, obj):
        # type: (AbstractObject) -> str
        from protocol0.lom.track.AbstractTrack import AbstractTrack
        from protocol0.lom.clip.Clip import Clip
        from protocol0.lom.device.DeviceParameter import DeviceParameter

        if isinstance(obj, AbstractTrack):
            return "_track"
        elif isinstance(obj, Clip):
            return "_clip"
        elif isinstance(obj, DeviceParameter):
            return "_device_parameter"
        else:
            raise Protocol0Error("Object of class %s is not a synchronizable object" % obj.__class__.__name__)

    def is_syncable(self, _):
        # type: (AbstractObject) -> bool
        return True

    def _sync_property(self, master, slave, property_name):
        # type: (AbstractObject, AbstractObject, str) -> None
        if not self.is_syncable(slave):
            return

        master_value = getattr(master, property_name)
        slave_value = getattr(slave, property_name)

        if not slave:
            return None

        if slave_value != master_value:
            setattr(slave, property_name, master_value)

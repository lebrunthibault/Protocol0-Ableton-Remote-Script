from functools import partial

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.clip.Clip import Clip


class ClipSynchronizer(AbstractControlSurfaceComponent):
    """ Class that handles the parameter sync of 2 clips """
    properties = ["name", "looping", "loop_start", "loop_end", "start_marker", "end_marker"]

    def __init__(self, master_clip, slave_clip, *a, **k):
        # type: (Clip, Clip) -> None
        super(ClipSynchronizer, self).__init__(*a, **k)
        # sync is two way but the master clip defines start values
        self.master_clip = master_clip
        self.slave_clip = slave_clip

        for property in self.properties:
            self.register_slot(master_clip._clip, self._sync_slave_properties, property)
            self.register_slot(slave_clip._clip, self._sync_master_properties, property)

        self._sync_slave_properties()

    def _sync_slave_properties(self):
        for property in self.properties:
            value = getattr(self.master_clip, property)
            if value is not None and getattr(self.slave_clip, property) != value:
                self.parent.defer(partial(setattr, self.slave_clip, property, value))

    def _sync_master_properties(self):
        for property in self.properties:
            value = getattr(self.slave_clip, property)
            if value is not None and getattr(self.master_clip, property) != value:
                self.parent.defer(partial(setattr, self.master_clip, property, value))



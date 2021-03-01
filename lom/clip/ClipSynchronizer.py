from typing import TYPE_CHECKING

from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    def __init__(self, master, slave, *a, **k):
        # type: (Clip, Clip) -> None
        super(ClipSynchronizer, self).__init__(master, slave, *a, **k)
        self.master = self.master  # type: Clip
        self.slave = self.slave  # type: Clip

        master.linked_clip = slave
        slave.linked_clip = master

        # noinspection PyUnresolvedReferences
        master.notify_linked()
        # noinspection PyUnresolvedReferences
        slave.notify_linked()

    def disconnect(self):
        super(ClipSynchronizer, self).disconnect()
        self.master.linked_clip = self.slave.linked_clip = None

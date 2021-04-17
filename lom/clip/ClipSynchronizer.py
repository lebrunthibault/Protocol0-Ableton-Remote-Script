from typing import TYPE_CHECKING, List

from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    def __init__(self, master, slave, *a, **k):
        # type: (Clip, Clip) -> None
        properties = ["loop_start", "loop_end", "start_marker", "end_marker"]
        super(ClipSynchronizer, self).__init__(
            master,
            slave,
            "_clip",
            listenable_properties=["name"] + properties,
            properties=["base_name"] + properties,
            *a,
            **k
        )
        self.master = self.master  # type: Clip
        self.slave = self.slave  # type: Clip

        master.linked_clip = slave
        slave.linked_clip = master

        # slave.clip_name = master.clip_name  # because clips are synchronized

        # noinspection PyUnresolvedReferences
        master.notify_linked()
        # noinspection PyUnresolvedReferences
        slave.notify_linked()

    def get_syncable_properties(self, changed_clip):
        # type: (Clip) -> List[str]
        if hasattr(changed_clip, "warping") and not changed_clip.warping:
            return ["base_name"]
        else:
            return self.properties

    def disconnect(self):
        super(ClipSynchronizer, self).disconnect()
        self.master.linked_clip = self.slave.linked_clip = None

from typing import TYPE_CHECKING, List, Any, Optional

from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer

if TYPE_CHECKING:
    from protocol0.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    """ For ExternalSynthTrack """

    def __init__(self, master, slave, *a, **k):
        # type: (Clip, Clip, Any, Any) -> None
        properties = ["loop_start", "loop_end", "start_marker", "end_marker"]
        self._syncable_properties = ["base_name"] + properties
        super(ClipSynchronizer, self).__init__(
            master,
            slave,
            "_clip",
            listenable_properties=["name"] + properties,
            *a,
            **k
        )
        self.master = self.master  # type: Optional[Clip]
        self.slave = self.slave  # type: Optional[Clip]

        # noinspection PyUnresolvedReferences
        master.notify_linked()
        # noinspection PyUnresolvedReferences
        slave.notify_linked()

    def get_syncable_properties(self, changed_clip):
        # type: (Clip) -> List[str]
        if hasattr(changed_clip, "warping") and not changed_clip.warping:
            return ["base_name"]
        else:
            return self._syncable_properties

    def disconnect(self):
        # type: () -> None
        super(ClipSynchronizer, self).disconnect()
        self.master = self.slave = None

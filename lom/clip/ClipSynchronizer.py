from typing import TYPE_CHECKING, List, Any, Optional

from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer
from protocol0.utils.log import log_ableton

if TYPE_CHECKING:
    from protocol0.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    """ For ExternalSynthTrack """

    def __init__(self, master, slave, *a, **k):
        # type: (Clip, Clip, Any, Any) -> None
        properties = ["muted", "loop_start", "loop_end", "start_marker", "end_marker"]

        if master.length != slave.length:
            log_ableton("clips %s of track %s cannot be loop synchronized because of unequal length" % (
                master, master.track.abstract_track), level=LogLevelEnum.WARNING)
            properties = ["muted"]

        # if slave.start_marker != slave.loop_start:
        #     properties = ["muted"]

        self._syncable_properties = ["base_name"] + properties
        super(ClipSynchronizer, self).__init__(
            master,
            slave,
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

    def is_syncable(self, clip):
        # type: (Clip) -> bool
        return not clip.track.is_recording

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

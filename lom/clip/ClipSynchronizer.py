from typing import TYPE_CHECKING, Any, Optional

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

        super(ClipSynchronizer, self).__init__(
            master,
            slave,
            listenable_properties=["name"] + properties,
            *a,
            **k
        )
        self.master = self.master  # type: Optional[Clip]
        self.slave = self.slave  # type: Optional[Clip]

    def is_syncable(self, clip):
        # type: (Clip) -> bool
        return not clip.track.is_recording

    def disconnect(self):
        # type: () -> None
        super(ClipSynchronizer, self).disconnect()
        self.master = self.slave = None

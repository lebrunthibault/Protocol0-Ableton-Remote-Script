from _Framework.CompoundElement import subject_slot_group
from typing import TYPE_CHECKING

from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class TrackSynchronizer(ObjectSynchronizer):
    def __init__(self, master, slave, *a, **k):
        # type: (SimpleTrack, SimpleTrack) -> None
        super(TrackSynchronizer, self).__init__(master, slave, "_track", *a, **k)
        self.master = self.master  # type: SimpleTrack
        self.slave = self.slave  # type: SimpleTrack

        master.linked_track = slave
        slave.linked_track = master

        self._fired_slot_index_listener.replace_subjects([master, slave])

    @subject_slot_group("fired_slot_index")
    def _fired_slot_index_listener(self, track):
        # type: (SimpleTrack) -> None
        """ Stops linked track on track stop """
        if track.fired_slot_index == -2 and track.linked_track.is_playing and not track.is_recording and not track.linked_track.is_recording:
            track.linked_track.stop()

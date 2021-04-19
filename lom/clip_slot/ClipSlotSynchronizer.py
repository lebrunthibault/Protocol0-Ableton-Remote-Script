from typing import Optional, TYPE_CHECKING, Any

from _Framework.CompoundElement import subject_slot_group
from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer
from a_protocol_0.lom.clip.ClipSynchronizer import ClipSynchronizer

if TYPE_CHECKING:
    from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot


class ClipSlotSynchronizer(ObjectSynchronizer):
    def __init__(self, master, slave, *a, **k):
        # type: (ClipSlot, ClipSlot, Any, Any) -> None
        super(ClipSlotSynchronizer, self).__init__(master, slave, "_clip_slot", *a, **k)
        self.master = self.master  # type: ClipSlot
        self.slave = self.slave  # type: ClipSlot

        master.linked_clip_slot = slave
        slave.linked_clip_slot = master
        self._map_clip_listener.replace_subjects([master, slave])
        self._is_triggered_listener.replace_subjects([master, slave])
        self._clip_synchronizer = None  # type: Optional[ClipSynchronizer]
        self._map_clip_listener(master)

    @subject_slot_group("map_clip")
    def _map_clip_listener(self, clip_slot):
        # type: (ClipSlot) -> None
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()
        if self.master.clip and self.slave.clip:
            with self.parent.component_guard():
                self._clip_synchronizer = ClipSynchronizer(master=self.master.clip, slave=self.slave.clip)
        else:
            self._clip_synchronizer = None

        if not clip_slot.clip and clip_slot.linked_clip_slot.clip:
            from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack

            if isinstance(clip_slot.track.abstract_group_track, ExternalSynthTrack) and clip_slot.track.is_audio:
                return
            clip_slot.linked_clip_slot.clip.delete()

    @subject_slot_group("is_triggered")
    def _is_triggered_listener(self, clip_slot):
        # type: (ClipSlot) -> None
        if not clip_slot.is_triggered:
            return

        if clip_slot.clip and clip_slot.linked_clip_slot.clip and not clip_slot.linked_clip_slot.is_triggered:
            clip_slot.linked_clip_slot.clip.is_playing = True
            return

        if not clip_slot.clip and not clip_slot.track.is_armed:
            clip_slot.linked_clip_slot.track.stop()

    def disconnect(self):
        # type: () -> None
        super(ClipSlotSynchronizer, self).disconnect()
        self.master.linked_clip_slot = self.slave.linked_clip_slot = None
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()

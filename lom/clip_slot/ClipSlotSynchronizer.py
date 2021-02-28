from typing import TYPE_CHECKING

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot


class ClipSlotSynchronizer(AbstractControlSurfaceComponent):
    """ Class that handles the linking of 2 clips (usually audio / midi)"""

    def __init__(self, clip_slot, *a, **k):
        # type: (ClipSlot) -> None
        super(ClipSlotSynchronizer, self).__init__(*a, **k)
        self._clip_synchronizer = None  # type: ObjectSynchronizer
        self.clip_slot = clip_slot
        self._is_triggered_listener.subject = self.clip_slot._clip_slot

    @property
    def linked_clip_slot(self):
        """ in property because at __init__ time the linked clip slot may not be instantiated """
        return self.clip_slot.track.linked_track.clip_slots[self.clip_slot.index]

    @property
    def clip_synchronizer(self):
        return self.linked_clip_slot._clip_slot_synchronizer._clip_synchronizer or self._clip_synchronizer

    @clip_synchronizer.setter
    def clip_synchronizer(self, clip_synchronizer):
        if self.clip_synchronizer:
            self.clip_synchronizer.disconnect()
        self._clip_synchronizer = clip_synchronizer
        if self.linked_clip_slot._clip_slot_synchronizer.clip_synchronizer:
            self.linked_clip_slot._clip_slot_synchronizer.clip_synchronizer.disconnect()
        self.linked_clip_slot._clip_slot_synchronizer._clip_synchronizer = clip_synchronizer

    def _has_clip_listener(self):
        if not self.clip_slot.has_clip:
            self.clip_synchronizer = None
            # auto delete linked clip on suppression
            if self.linked_clip_slot.has_clip:
                self.linked_clip_slot.clip.delete()
        else:
            if self.linked_clip_slot.clip:
                self.clip_synchronizer = ObjectSynchronizer(
                    self.clip_slot.clip, self.linked_clip_slot.clip, "_clip",
                    ["name", "looping", "loop_start", "loop_end",
                     "start_marker", "end_marker"])

    @p0_subject_slot("is_triggered")
    def _is_triggered_listener(self):
        if self.clip_slot.is_triggered and not self.linked_clip_slot.is_triggered and self.clip_slot.clip and self.linked_clip_slot.clip:
            self.linked_clip_slot.clip.is_playing = True
        elif not self.clip_slot.clip:
            self.linked_clip_slot.track.stop()

    def disconnect(self):
        super(ClipSlotSynchronizer, self).disconnect()
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()

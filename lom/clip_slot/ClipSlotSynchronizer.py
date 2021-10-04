from typing import Optional, TYPE_CHECKING, Any

from _Framework.CompoundElement import subject_slot_group
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.clip.ClipSynchronizer import ClipSynchronizer

if TYPE_CHECKING:
    from protocol0.lom.clip_slot.ClipSlot import ClipSlot


class ClipSlotSynchronizer(AbstractControlSurfaceComponent):
    """ For ExternalSynthTrack """

    def __init__(self, midi_cs, audio_cs, *a, **k):
        # type: (ClipSlot, ClipSlot, Any, Any) -> None
        super(ClipSlotSynchronizer, self).__init__(*a, **k)
        self.midi_cs = midi_cs
        self.audio_cs = audio_cs

        self._has_clip_listener.replace_subjects([midi_cs, audio_cs])
        self._is_triggered_listener.replace_subjects([midi_cs, audio_cs])
        self._clip_synchronizer = None  # type: Optional[ClipSynchronizer]
        self._has_clip_listener(midi_cs)

    def linked_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> ClipSlot
        return self.audio_cs if clip_slot == self.midi_cs else self.audio_cs

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, changed_clip_slot):
        # type: (ClipSlot) -> None
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()
        if self.midi_cs.clip and self.audio_cs.clip:
            with self.parent.component_guard():
                self._clip_synchronizer = ClipSynchronizer(master=self.midi_cs.clip, slave=self.audio_cs.clip)
        else:
            self._clip_synchronizer = None

        linked_clip_slot = self.linked_clip_slot(clip_slot=changed_clip_slot)

        if not changed_clip_slot.clip and linked_clip_slot.clip:
            # self.song.end_undo_step()
            linked_clip_slot.clip.delete()

    @subject_slot_group("is_triggered")
    def _is_triggered_listener(self, changed_clip_slot):
        # type: (ClipSlot) -> None
        if not changed_clip_slot.is_triggered:
            return

        linked_clip_slot = self.linked_clip_slot(clip_slot=changed_clip_slot)

        if changed_clip_slot.clip and linked_clip_slot.clip and not linked_clip_slot.is_triggered:
            linked_clip_slot.clip.is_playing = True
            return

        if not changed_clip_slot.clip and not changed_clip_slot.track.is_armed:
            linked_clip_slot.track.stop()

    def disconnect(self):
        # type: () -> None
        super(ClipSlotSynchronizer, self).disconnect()
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()
            self._clip_synchronizer = None

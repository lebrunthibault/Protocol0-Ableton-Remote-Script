from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.utils.decorators import has_callback_queue

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationMidiClipSlot(ClipSlot):
    def __init__(self, *a, **k):
        super(AutomationMidiClipSlot, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationMidiTrack
        self.register_slot(self._clip_slot, self._has_clip_listener, "has_clip")  # allows subclassing
        # self._has_clip_listener.subject = self._clip_slot

    # @subject_slot("has_clip")
    @has_callback_queue
    def _has_clip_listener(self):
        self.parent.log_debug("has_clip in AutomationMidiClipSlot")
        return
        automated_clip_slot = self.track.clip_slots[self.index]
        if not self.has_clip and automated_clip_slot.has_clip:
            self.track.clip_slots[self.index].clip.delete()
            return
        if self.has_clip and not automated_clip_slot.has_clip:
            automated_clip_slot.insert_dummy_clip()
            return

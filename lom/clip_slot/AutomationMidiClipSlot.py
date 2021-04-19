from functools import partial

from typing import TYPE_CHECKING, Any

from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationMidiClipSlot(ClipSlot):
    """ special automation handling : the dummy audio clip is created on midi clip creation """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AutomationMidiClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: AutomationMidiClip
        self.track = self.track  # type: AutomationMidiTrack

    @p0_subject_slot("has_clip")
    def _has_clip_listener(self):
        # type: () -> None
        super(AutomationMidiClipSlot, self)._has_clip_listener()
        if self.clip and self.linked_clip_slot and not self.linked_clip_slot.clip:
            self.parent.defer(partial(self.linked_clip_slot.insert_dummy_clip, name=self.clip.name))

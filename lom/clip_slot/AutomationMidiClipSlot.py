from typing import TYPE_CHECKING

from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationMidiClipSlot(ClipSlot):
    """ special automation handling : the dummy audio clip is created on midi clip creation """
    def __init__(self, *a, **k):
        super(AutomationMidiClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: AutomationMidiClip

    @p0_subject_slot("has_clip")
    def _has_clip_listener(self):
        super(AutomationMidiClipSlot, self)._has_clip_listener()

        if self.clip and not self.linked_clip_slot.clip:
            seq = Sequence(silent=True).add(wait=1)
            seq.add(self.linked_clip_slot.insert_dummy_clip, do_if=lambda: not self.linked_clip_slot.has_clip)
            return seq.done()

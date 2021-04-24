from typing import TYPE_CHECKING, Any

from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationMidiClipSlot(ClipSlot):
    """ special automation handling : the dummy audio clip is created on midi clip creation """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AutomationMidiClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: AutomationMidiClip
        self.track = self.track  # type: AutomationMidiTrack

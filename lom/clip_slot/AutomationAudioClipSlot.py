from typing import TYPE_CHECKING

from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
    from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot


class AutomationAudioClipSlot(ClipSlot):
    def __init__(self, *a, **k):
        super(AutomationAudioClipSlot, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationAudioTrack
        self.clip = self.clip  # type: AutomationAudioClip
        self._has_clip_listener.subject = self._clip_slot
        self.automated_midi_clip_slot = None  # type: AutomationMidiClipSlot

    def _connect(self, clip_slot):
        # type: (AutomationMidiClipSlot) -> None
        self.automated_midi_clip_slot = clip_slot

    @subject_slot("has_clip")
    def _has_clip_listener(self):
        super(AutomationAudioClipSlot, self)._has_clip_listener()
        seq = Sequence().add(wait=1)

        if not self.has_clip and self.automated_midi_clip_slot and self.automated_midi_clip_slot.has_clip:
            seq.add(self.automated_midi_clip_slot.clip.delete)

        return seq.done()

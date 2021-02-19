from typing import TYPE_CHECKING

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
    from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot


class AutomationMidiClipSlot(ClipSlot):
    def __init__(self, *a, **k):
        super(AutomationMidiClipSlot, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationMidiTrack
        self.clip = self.clip  # type: AutomationMidiClip
        self._has_clip_listener.subject = self._clip_slot
        self.automated_audio_clip_slot = None  # type: AutomationAudioClipSlot

    def _connect(self, clip_slot):
        # type: (AutomationAudioClipSlot) -> None
        if not clip_slot:
            raise Protocol0Error("Inconsistent clip_slot state for %s (%s)" % (self, self.track))
        self.automated_audio_clip_slot = clip_slot
        clip_slot._connect(self)

    @p0_subject_slot("has_clip")
    def _has_clip_listener(self):
        super(AutomationMidiClipSlot, self)._has_clip_listener()

        if not self.automated_audio_clip_slot:
            return

        seq = Sequence().add(wait=1)
        if self.has_clip:
            if not self.clip.name:
                self.clip.name = "%s *" % self.track.automated_audio_track.automated_parameter.full_name
            if self.automated_audio_clip_slot.has_clip:
                self.clip._connect(self.automated_audio_clip_slot.clip)
            else:
                seq.add(self.automated_audio_clip_slot.insert_dummy_clip)
                seq.add(lambda: self.clip._connect(self.automated_audio_clip_slot.clip),
                        name="connect to audio clip slot")
        elif self.automated_audio_clip_slot.has_clip:
            seq.add(self.automated_audio_clip_slot.clip.delete)

        return seq.done()

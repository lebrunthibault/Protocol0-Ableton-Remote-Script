from typing import TYPE_CHECKING

from a_protocol_0.lom.clip.Clip import Clip

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
    from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationAudioClip(Clip):
    def __init__(self, *a, **k):
        super(AutomationAudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationAudioTrack
        self.clip_slot = self.clip_slot  # type: AutomationAudioClipSlot
        self.automated_midi_clip = None  # type: AutomationMidiClip

    def _connect(self, clip):
        # type: (AutomationMidiClip) -> None
        self.automated_midi_clip = clip

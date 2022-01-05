from typing import Any, TYPE_CHECKING, Optional

from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip.MidiClip import MidiClip

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
    from protocol0.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot


class AudioTailClip(AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioTailClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleAudioTailTrack
        self.clip_slot = self.clip_slot  # type: AudioTailClipSlot

    @property
    def midi_clip(self):
        # type: () -> Optional[MidiClip]
        return self.track.abstract_group_track.midi_track.clip_slots[self.index].clip

from typing import Any, List, Type, cast

from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class SimpleAudioTailTrack(SimpleAudioTrack):
    DEFAULT_NAME = "tail"
    CLIP_SLOT_CLASS = AudioTailClipSlot  # type: Type[AudioClipSlot]

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack

        self.abstract_group_track = cast(ExternalSynthTrack, self.abstract_group_track)

    @property
    def clip_slots(self):
        # type: () -> List[AudioTailClipSlot]
        return cast(List[AudioTailClipSlot], super(SimpleAudioTailTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioTailClip]
        return cast(List[AudioTailClip], super(SimpleAudioTailTrack, self).clips)

    def configure(self):
        # type: () -> None
        try:
            self.input_routing.track = self.abstract_group_track.midi_track
            self.input_routing.channel = InputRoutingChannelEnum.POST_FX
        except Protocol0Error:
            return

from typing import Any, TYPE_CHECKING, List

from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class SimpleAudioTailTrack(SimpleAudioTrack):
    DEFAULT_NAME = "tail"
    CLIP_SLOT_CLASS = AudioTailClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        self.abstract_group_track = self.abstract_group_track  # type: ExternalSynthTrack
        self.clip_slots = self.clip_slots  # type: List[AudioTailClipSlot]

    @property
    def clips(self):
        # type: () -> List[AudioTailClipSlot]
        return super(SimpleAudioTailTrack, self).clips  # type: ignore

    def configure(self):
        # type: () -> None
        try:
            self.input_routing_track = self.abstract_group_track.midi_track
            self.input_routing_channel = InputRoutingChannelEnum.POST_FX
        except Protocol0Error:
            return

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        super(SimpleAudioTailTrack, self)._devices_listener()
        if len(self.devices):
            self.parent.log_error("A tail track should not have devices")

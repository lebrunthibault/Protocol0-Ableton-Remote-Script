from typing import Any, TYPE_CHECKING, List

from protocol0.domain.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


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
            self.input_routing.track = self.abstract_group_track.midi_track
            self.input_routing.channel = InputRoutingChannelEnum.POST_FX
        except Protocol0Error:
            return

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        super(SimpleAudioTailTrack, self)._devices_listener()
        if len(self.devices):
            Logger.log_error("A tail track should not have devices")

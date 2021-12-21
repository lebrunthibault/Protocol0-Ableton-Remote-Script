from typing import Any, TYPE_CHECKING

from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class SimpleAudioTailTrack(SimpleAudioTrack):
    DEFAULT_NAME = "tail"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        self.abstract_group_track = self.abstract_group_track  # type: ExternalSynthTrack

    def configure(self):
        # type: () -> None
        self.input_routing_track = self.abstract_group_track.midi_track
        self.input_routing_channel = InputRoutingChannelEnum.POST_FX

    @p0_subject_slot("devices")
    def _devices_listener(self):
        # type: () -> None
        super(SimpleAudioTailTrack, self)._devices_listener()
        if len(self.devices):
            self.parent.log_error("A tail track should not have devices")

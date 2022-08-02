from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.validation.object_validators.SimpleTrackValidator import (
    SimpleTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import \
    PropertyValueValidator
from protocol0.domain.lom.validation.sub_validators.SimpleTrackHasDeviceValidator import \
    SimpleTrackHasDeviceValidator
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface


class SimpleMidiExtTrackValidator(SimpleTrackValidator):
    def __init__(self, track, browser_service):
        # type: (SimpleMidiExtTrack, BrowserServiceInterface) -> None
        self._track = track

        validators = [
            PropertyValueValidator(track, "volume", 0, name="midi track volume"),
            SimpleTrackHasDeviceValidator(
                track, DeviceEnum.EXTERNAL_AUDIO_EFFECT, browser_service
            ),
            PropertyValueValidator(
                track.input_routing,
                "type",
                InputRoutingTypeEnum.ALL_INS,
                "midi track input type",
            ),
            PropertyValueValidator(
                track.input_routing,
                "channel",
                InputRoutingChannelEnum.CHANNEL_1,
                name="midi track input channel",
            ),
            PropertyValueValidator(
                track.output_routing,
                "type",
                OutputRoutingTypeEnum.SENDS_ONLY,
                name="midi track output type",
            ),
        ]

        super(SimpleMidiExtTrackValidator, self).__init__(track, validators)

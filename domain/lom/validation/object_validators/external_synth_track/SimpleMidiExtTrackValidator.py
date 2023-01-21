from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import \
    PropertyValueValidator
from protocol0.domain.lom.validation.sub_validators.SimpleTrackHasDeviceValidator import \
    SimpleTrackHasDeviceValidator
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.Config import Config


class SimpleMidiExtTrackValidator(AggregateValidator):
    def __init__(self, track, browser_service):
        # type: (SimpleMidiExtTrack, BrowserServiceInterface) -> None
        self._track = track

        validators = [
            PropertyValueValidator(track, "volume", Config.ZERO_DB_VOLUME, name="midi track volume"),
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
                track.group_track,
                name="midi track output type",
            ),
        ]

        super(SimpleMidiExtTrackValidator, self).__init__(validators)

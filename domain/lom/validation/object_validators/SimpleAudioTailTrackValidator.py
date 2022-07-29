from typing import cast, List

from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import (
    SimpleAudioTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)


class SimpleAudioTailTrackValidator(SimpleAudioTrackValidator):
    def __init__(self, track):
        # type: (SimpleAudioTailTrack) -> None
        ext_track = cast(ExternalSynthTrack, track.abstract_group_track)
        validators = cast(
            List[ValidatorInterface],
            [
                PropertyValueValidator(
                    track.input_routing,
                    "track",
                    ext_track.midi_track,
                    name="tail track input track",
                ),
                PropertyValueValidator(
                    track.input_routing,
                    "channel",
                    InputRoutingChannelEnum.POST_FX,
                    name="tail track input channel",
                ),
            ],
        )
        for clip in track.clips:
            validators.append(PropertyValueValidator(clip, "muted", True))

        super(SimpleAudioTailTrackValidator, self).__init__(track, validators=validators)

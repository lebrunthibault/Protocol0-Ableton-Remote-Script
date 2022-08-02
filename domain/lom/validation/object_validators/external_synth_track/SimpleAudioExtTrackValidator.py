from typing import List

from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import \
    SimpleAudioTrackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import \
    PropertyValueValidator


class SimpleAudioExtTrackValidator(SimpleAudioTrackValidator):
    def __init__(self, track, midi_track):
        # type: (SimpleAudioExtTrack, SimpleMidiExtTrack) -> None
        self._track = track
        self._midi_track = midi_track

        validators = [
            PropertyValueValidator(track, "volume", 0, name="audio track volume"),
            PropertyValueValidator(
                track.input_routing,
                "track",
                self._midi_track,
                name="audio track input track",
            ),
            PropertyValueValidator(
                track.input_routing,
                "channel",
                InputRoutingChannelEnum.POST_FX,
                name="audio track input channel",
            ),
        ]  # type: List[ValidatorInterface]

        super(SimpleAudioExtTrackValidator, self).__init__(track, validators)

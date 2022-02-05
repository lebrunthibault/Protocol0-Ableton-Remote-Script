from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import SimpleAudioTrackValidator
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import PropertyValueValidator


class SimpleAudioTailTrackValidator(AggregateValidator):
    def __init__(self, track):
        # type: (SimpleAudioTailTrack) -> None
        validators = SimpleAudioTrackValidator(track)._validators

        validators += [
            PropertyValueValidator(track.input_routing, "track", track.abstract_group_track.midi_track),
            PropertyValueValidator(track.input_routing, "channel",
                                   track.abstract_group_track.instrument.AUDIO_INPUT_ROUTING_CHANNEL),
        ]
        for clip in track.clips:
            validators.append(
                PropertyValueValidator(clip, "muted", True)
            )
        super(SimpleAudioTailTrackValidator, self).__init__(validators=validators)

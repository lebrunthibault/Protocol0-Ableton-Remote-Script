from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.validation.sub_validators.CallbackValidator import CallbackValidator


class SimpleAudioTrackValidator(AggregateValidator):
    def __init__(self, track):
        # type: (SimpleAudioTrack) -> None
        self._track = track
        validators = [
            CallbackValidator(track, lambda t: t.is_armable, None, "track should be armable"),
        ]

        super(SimpleAudioTrackValidator, self).__init__(validators)

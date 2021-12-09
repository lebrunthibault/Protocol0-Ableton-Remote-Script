from typing import Any

from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.validation.AbstractObjectValidator import AbstractObjectValidator
from protocol0.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.validation.sub_validators.CallbackValidator import CallbackValidator


class SimpleAudioTrackValidator(AbstractObjectValidator, AggregateValidator):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        self._track = track
        validators = [
            CallbackValidator(track, lambda t: t.is_armable, None, "track should be armable"),
        ]
        self._validators = validators  # type: ignore[assignment]
        super(SimpleAudioTrackValidator, self).__init__(track, *a, **k)

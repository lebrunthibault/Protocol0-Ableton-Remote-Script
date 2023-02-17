from typing import List, Optional

from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator


class SimpleAudioTrackValidator(AggregateValidator):
    def __init__(self, track, validators=None):
        # type: (SimpleAudioTrack, Optional[List[ValidatorInterface]]) -> None
        self._track = track

        if validators is None:
            validators = []

        validators += [
            CallbackValidator(
                track, lambda t: t.arm_state.is_armable, None, "%s should be armable" % track
            ),
        ]

        super(SimpleAudioTrackValidator, self).__init__(validators)

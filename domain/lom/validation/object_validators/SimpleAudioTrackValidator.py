from typing import List, Optional

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator


class SimpleAudioTrackValidator(AggregateValidator):
    def __init__(self, track, validators=None):
        # type: (SimpleAudioTrack, Optional[List[ValidatorInterface]]) -> None
        self._track = track

        if validators is None:
            validators = []

        valid_clip_colors = (
            track.appearance.computed_color,
            ClipColorEnum.AUDIO_UN_QUANTIZED.int_value,
        )
        validators += [
            CallbackValidator(
                track, lambda t: t.arm_state.is_armable, None, "%s should be armable" % track
            ),
            CallbackValidator(
                track,
                lambda t: all(clip.appearance.color in valid_clip_colors for clip in t.clips),
                None,
                "clips should have the right color",
            ),
        ]

        super(SimpleAudioTrackValidator, self).__init__(validators)

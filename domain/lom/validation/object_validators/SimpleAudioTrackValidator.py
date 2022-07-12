from typing import List, Optional

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.SimpleTrackValidator import \
    SimpleTrackValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator


class SimpleAudioTrackValidator(SimpleTrackValidator):
    def __init__(self, track, validators=None):
        # type: (SimpleAudioTrack, Optional[List[ValidatorInterface]]) -> None
        self._track = track

        if validators is None:
            validators = []

        valid_clip_colors = (
            track.appearance.computed_color,
            ClipColorEnum.AUDIO_UN_QUANTIZED.color_int_value,
        )
        validators += [
            CallbackValidator(
                track, lambda t: t.arm_state.is_armable, None, "track should be armable"
            ),
            CallbackValidator(
                track,
                lambda t: all(clip.appearance.color in valid_clip_colors for clip in t.clips),
                None,
                "clips should have the right color",
            ),
        ]  # type: List[ValidatorInterface]

        super(SimpleAudioTrackValidator, self).__init__(track, validators)

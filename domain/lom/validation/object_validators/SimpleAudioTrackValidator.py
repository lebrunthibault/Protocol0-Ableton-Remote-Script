from typing import List

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator


class SimpleAudioTrackValidator(AggregateValidator):
    def __init__(self, track):
        # type: (SimpleAudioTrack) -> None
        self._track = track
        valid_clip_colors = (track.computed_color, ClipColorEnum.AUDIO_UN_QUANTIZED.color_int_value)
        validators = [
            CallbackValidator(track, lambda t: t.is_armable, None, "track should be armable"),
            CallbackValidator(track, lambda t: all(clip.color in valid_clip_colors for clip in t.clips), None,
                              "clips should have the right color"),
        ]  # type: List[ValidatorInterface]

        super(SimpleAudioTrackValidator, self).__init__(validators)

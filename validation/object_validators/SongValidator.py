from typing import Any

import Live
from protocol0.lom.Song import Song
from protocol0.validation.AbstractObjectValidator import AbstractObjectValidator
from protocol0.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.validation.sub_validators.PropertyNotNullValidator import PropertyNotNullValidator
from protocol0.validation.sub_validators.PropertyValueValidator import PropertyValueValidator


class SongValidator(AbstractObjectValidator, AggregateValidator):
    def __init__(self, song, *a, **k):
        # type: (Song, Any, Any) -> None
        validators = [
            PropertyNotNullValidator(song, "usamo_track"),
            PropertyNotNullValidator(song, "template_dummy_clip"),
            PropertyValueValidator(song, "clip_trigger_quantization", Live.Song.Quantization.q_bar),
        ]
        self._validators = validators  # type: ignore[assignment]
        super(SongValidator, self).__init__(song, *a, **k)

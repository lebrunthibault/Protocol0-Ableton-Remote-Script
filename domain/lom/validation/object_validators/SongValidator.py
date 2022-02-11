from typing import TYPE_CHECKING

import Live
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.PropertyNotNullValidator import PropertyNotNullValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import PropertyValueValidator
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class SongValidator(AggregateValidator):
    def __init__(self, song):
        # type: (Song) -> None
        validators = [
            PropertyNotNullValidator(SongFacade, "usamo_track"),
            PropertyNotNullValidator(SongFacade, "template_dummy_clip"),
            PropertyValueValidator(song, "clip_trigger_quantization", Live.Song.Quantization.q_bar),
        ]
        super(SongValidator, self).__init__(validators=validators)

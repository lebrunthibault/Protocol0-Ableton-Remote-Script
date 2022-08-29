from typing import List, Optional

from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator


class AbstractGroupTrackValidator(AggregateValidator):
    def __init__(self, track, validators=None):
        # type: (AbstractGroupTrack, Optional[List[ValidatorInterface]]) -> None
        if validators is None:
            validators = []

        validators.append(track.dummy_group.make_validator())

        super(AbstractGroupTrackValidator, self).__init__(validators)

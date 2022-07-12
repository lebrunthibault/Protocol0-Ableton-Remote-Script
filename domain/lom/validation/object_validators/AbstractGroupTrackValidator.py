from typing import List, Optional

from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.SimpleDummyReturnTrackValidator import (
    SimpleDummyReturnTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.SimpleDummyTrackValidator import (
    SimpleDummyTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator


class AbstractGroupTrackValidator(AggregateValidator):
    def __init__(self, track, validators=None):
        # type: (AbstractGroupTrack, Optional[List[ValidatorInterface]]) -> None
        self._track = track

        if validators is None:
            validators = []

        # DUMMY TRACK
        if track.dummy_track is not None:
            validators.append(SimpleDummyTrackValidator(track.dummy_track))

        # DUMMY RETURN TRACK
        if track.dummy_return_track is not None:
            validators.append(SimpleDummyReturnTrackValidator(track.dummy_return_track))

        super(AbstractGroupTrackValidator, self).__init__(validators)

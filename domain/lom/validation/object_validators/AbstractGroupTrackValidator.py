from typing import List, Optional

from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyReturnTrackValidator import (
    SimpleDummyReturnTrackValidator,
)
from protocol0.domain.lom.validation.object_validators.external_synth_track.SimpleDummyTrackValidator import (
    SimpleDummyTrackValidator,
)
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)


class AbstractGroupTrackValidator(AggregateValidator):
    def __init__(self, track, validators=None):
        # type: (AbstractGroupTrack, Optional[List[ValidatorInterface]]) -> None
        self._track = track

        if validators is None:
            validators = []

        for sub_track in track.sub_tracks:
            if sub_track != track.dummy_track and sub_track != track.dummy_return_track:
                validators.append(
                    PropertyValueValidator(
                        sub_track.output_routing,
                        "track",
                        track.dummy_track or track.base_track,
                        name="track output routing",
                    ),
                )

        # DUMMY TRACK
        if track.dummy_track is not None:
            validators.append(SimpleDummyTrackValidator(track.dummy_track))

        # DUMMY RETURN TRACK
        if track.dummy_return_track is not None:
            validators.append(SimpleDummyReturnTrackValidator(track.dummy_return_track))

        super(AbstractGroupTrackValidator, self).__init__(validators)

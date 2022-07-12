from typing import List, Optional

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)
from protocol0.shared.SongFacade import SongFacade


class SimpleTrackValidator(AggregateValidator):
    def __init__(self, track, validators=None):
        # type: (SimpleTrack, Optional[List[ValidatorInterface]]) -> None
        self._track = track

        if validators is None:
            validators = []

        # only valid for lone tracks
        if track.abstract_group_track is None:
            validators.append(
                PropertyValueValidator(
                    track.output_routing,
                    "track",
                    track.base_track.group_track or SongFacade.master_track(),
                    name="group track output routing",
                    ),
            )

        super(SimpleTrackValidator, self).__init__(validators)

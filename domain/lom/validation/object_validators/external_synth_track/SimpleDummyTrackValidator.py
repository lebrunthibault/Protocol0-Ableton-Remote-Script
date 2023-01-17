from typing import List

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)


class SimpleDummyTrackValidator(AggregateValidator):
    def __init__(self, track):
        # type: (SimpleDummyTrack) -> None
        self._track = track

        validators = [
            PropertyValueValidator(track, "volume", 0),
            PropertyValueValidator(
                track, "current_monitoring_state", CurrentMonitoringStateEnum.IN
            ),
            PropertyValueValidator(track.input_routing, "type", InputRoutingTypeEnum.NO_INPUT),
            PropertyValueValidator(track.output_routing, "track", track.group_track),
        ]  # type: List[ValidatorInterface]

        super(SimpleDummyTrackValidator, self).__init__(validators)

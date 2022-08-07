from typing import List

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)


class SimpleDummyReturnTrackValidator(AggregateValidator):
    def __init__(self, track):
        # type: (SimpleDummyReturnTrack) -> None
        self._track = track

        validators = [
            PropertyValueValidator(track, "volume", 0),
            PropertyValueValidator(
                track, "current_monitoring_state", CurrentMonitoringStateEnum.IN
            ),
            PropertyValueValidator(track.input_routing, "track", track.group_track),
            PropertyValueValidator(track.output_routing, "type", OutputRoutingTypeEnum.SENDS_ONLY),
        ]  # type: List[ValidatorInterface]

        for clip in track.clips:
            validators.append(PropertyValueValidator(clip.loop, "looping", True))

        super(SimpleDummyReturnTrackValidator, self).__init__(validators)

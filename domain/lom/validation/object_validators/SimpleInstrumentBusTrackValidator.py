from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.InstrumentBusTrack import InstrumentBusTrack
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)


class SimpleInstrumentBusTrackValidator(AggregateValidator):
    def __init__(self, track):
        # type: (InstrumentBusTrack) -> None
        validators = [
            PropertyValueValidator(track.input_routing, "type", InputRoutingTypeEnum.NO_INPUT),
            PropertyValueValidator(
                track, "current_monitoring_state", CurrentMonitoringStateEnum.IN
            ),
            CallbackValidator(
                track, lambda t: len(t.clips) == 1, None, "track should have one empty dummy clip"
            ),
        ]

        if len(track.clips) != 0:
            validators.append(
                CallbackValidator(
                    track,
                    lambda t: t.clips[0].muted,
                    lambda t: setattr(t.clips[0], "muted", True),
                    "dummy clip should be muted",
                )
            )

        super(SimpleInstrumentBusTrackValidator, self).__init__(validators)

from typing import List

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.external_synth_track.DummyClipValidator import \
    DummyClipValidator
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
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
            CallbackValidator(
                track,
                lambda c: len(list(track.devices)) == 0,
                self._remove_devices,
                "%s should have no devices. Got %s" % (track, len(track.devices)),
            ),
        ]  # type: List[ValidatorInterface]

        for clip in track.clips:
            validators += DummyClipValidator(clip, track.devices)._validators

        super(SimpleDummyReturnTrackValidator, self).__init__(validators)

    def _remove_devices(self, track):
        # type: (SimpleDummyReturnTrack) -> None
        for device in track.devices:
            track.devices.delete(device)

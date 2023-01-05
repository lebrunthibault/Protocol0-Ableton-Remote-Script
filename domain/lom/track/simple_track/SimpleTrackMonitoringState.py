from typing import TYPE_CHECKING

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.MonitoringStateInterface import MonitoringStateInterface
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack


class SimpleTrackMonitoringState(MonitoringStateInterface):
    def __init__(self, track):
        # type: (AbstractTrack) -> None
        self._track = track

    def switch(self):
        # type: () -> None
        from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack

        if self._track.current_monitoring_state == CurrentMonitoringStateEnum.AUTO:
            if isinstance(self._track, SimpleAudioTrack):
                self._track.input_routing.type = InputRoutingTypeEnum.EXT_IN
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        else:
            if isinstance(self._track, SimpleAudioTrack):
                self._track.input_routing.type = InputRoutingTypeEnum.NO_INPUT
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

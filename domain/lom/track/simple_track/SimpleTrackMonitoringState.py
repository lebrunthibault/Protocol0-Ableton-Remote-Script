from typing import TYPE_CHECKING

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleTrackMonitoringState(object):
    def __init__(self, track):
        # type: (SimpleTrack) -> None
        self._track = track

    def switch(self):
        # type: () -> None
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        if self._track.current_monitoring_state == CurrentMonitoringStateEnum.AUTO:
            if isinstance(self._track, SimpleAudioTrack):
                self._track.input_routing.type = InputRoutingTypeEnum.EXT_IN  # type: ignore[has-type]
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        else:
            if isinstance(self._track, SimpleAudioTrack):
                self._track.input_routing.type = InputRoutingTypeEnum.NO_INPUT  # type: ignore[has-type]
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

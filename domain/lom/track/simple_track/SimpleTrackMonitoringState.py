import Live

from protocol0.domain.lom.track.MonitoringStateInterface import MonitoringStateInterface


class SimpleTrackMonitoringState(MonitoringStateInterface):
    def __init__(self, live_track):
        # type: (Live.Track.Track) -> None
        self._live_track = live_track

    def switch(self):
        # type: () -> None
        if self._live_track.current_monitoring_state == Live.Track.Track.monitoring_states.AUTO:
            self._live_track.current_monitoring_state = Live.Track.Track.monitoring_states.IN
        else:
            self._live_track.current_monitoring_state = Live.Track.Track.monitoring_states.AUTO

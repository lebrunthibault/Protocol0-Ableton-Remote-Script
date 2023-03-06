from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.ext_track.ExtArmState import (
    ExtArmState,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.observer.Observable import Observable


class ExtMonitoringState(Observable):
    def __init__(self, base_track):
        # type: (SimpleAudioTrack) -> None
        super(ExtMonitoringState, self).__init__()
        self._midi_track = base_track.sub_tracks[0]
        self._audio_track = base_track.sub_tracks[1]

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, ExtArmState):
            if observable.is_armed:
                self.monitor_midi()
            else:
                self.monitor_audio()

    def switch(self):
        # type: () -> None
        if self._midi_track.muted:
            assert self._midi_track.arm_state.is_armed, "Please arm the track first"
            self.monitor_midi()
        else:
            self.monitor_audio()

        self.notify_observers()

    def monitor_midi(self):
        # type: () -> None
        self._midi_track.muted = False
        # if self._midi_track.instrument is not None:
        #     self._midi_track.instrument.device.is_enabled = True

        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._audio_track._output_meter_level_listener.subject = self._audio_track._track

    def monitor_audio(self):
        # type: () -> None
        self._midi_track.muted = True
        if self._midi_track.instrument is not None:
            self._midi_track.instrument.device.is_enabled = False

        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        self._audio_track._output_meter_level_listener.subject = None

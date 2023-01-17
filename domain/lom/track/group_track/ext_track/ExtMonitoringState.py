from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.dummy_group.DummyGroup import DummyGroup
from protocol0.domain.lom.track.group_track.ext_track.ExtArmState import (
    ExtArmState,
)
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.observer.Observable import Observable


class ExtMonitoringState(Observable):
    def __init__(self, base_track, dummy_group):
        # type: (SimpleAudioTrack, DummyGroup) -> None
        super(ExtMonitoringState, self).__init__()
        self._midi_track = base_track.sub_tracks[0]
        self._audio_track = base_track.sub_tracks[1]
        self._dummy_group = dummy_group

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
        # midi track
        self._un_mute_track(self._midi_track)

        # audio track
        self._mute_track(self._audio_track)
        self._audio_track._output_meter_level_listener.subject = self._audio_track._track

        # switch solo
        if self._audio_track.solo:
            self._midi_track.solo = True
            self._audio_track.solo = False

    # noinspection DuplicatedCode
    def monitor_audio(self):
        # type: () -> None
        # midi track
        self._midi_track.muted = True
        self._midi_track.current_monitoring_state = CurrentMonitoringStateEnum.OFF
        self._midi_track.output_routing.type = OutputRoutingTypeEnum.SENDS_ONLY

        # audio track
        self._un_mute_track(self._audio_track)
        self._audio_track._output_meter_level_listener.subject = None

        # switch solo
        if self._midi_track.solo:
            self._audio_track.solo = True
            self._midi_track.solo = False

    def _mute_track(self, track):
        # type: (SimpleTrack) -> None
        track.muted = True
        track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        track.output_routing.type = OutputRoutingTypeEnum.SENDS_ONLY

    def _un_mute_track(self, track):
        # type: (SimpleTrack) -> None
        track.muted = False
        track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        track.output_routing.track = self._dummy_group.input_routing_track

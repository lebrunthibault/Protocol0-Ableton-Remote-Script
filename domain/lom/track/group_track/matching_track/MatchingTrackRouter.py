import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.observer.Observable import Observable


class MatchingTrackRouter(SlotManager):
    def __init__(self, base_track, audio_track):
        # type: (SimpleTrack, SimpleAudioTrack) -> None
        super(MatchingTrackRouter, self).__init__()
        self._base_track = base_track
        self._audio_track = audio_track
        base_track.arm_state.register_observer(self)
        self._name_listener.replace_subjects([self._base_track._track, self._audio_track._track])

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, AbstractTrackArmState):
            if observable.is_armed:
                self.monitor_base_track()
            else:
                self.monitor_audio_track()

    def monitor_base_track(self):
        # type: () -> None
        if not liveobj_valid(self._base_track._track) or not liveobj_valid(self._audio_track._track):
            return None

        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._audio_track.input_routing.type = InputRoutingTypeEnum.NO_INPUT
        self._base_track.output_routing.track = self._audio_track

    def monitor_audio_track(self):
        # type: () -> None
        """Restore the current monitoring state of the track"""
        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

    @subject_slot_group("name")
    @defer
    def _name_listener(self, _):
        # type: (Live.Track.Track) -> None
        """on any name change, cut the link"""
        self.disconnect()

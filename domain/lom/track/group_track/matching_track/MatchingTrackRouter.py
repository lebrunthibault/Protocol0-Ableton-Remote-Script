from argparse import ArgumentError

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackProxy import \
    MatchingTrackProxy
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.observer.Observable import Observable


class MatchingTrackRouter(SlotManager):
    def __init__(self, track_proxy):
        # type: (MatchingTrackProxy) -> None
        super(MatchingTrackRouter, self).__init__()
        self._track_proxy = track_proxy
        track_proxy.base_track.arm_state.register_observer(self)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, MatchingTrackProxy):
            tracks = [self._track_proxy.base_track._track, self._track_proxy.audio_track._track]
            self._name_listener.replace_subjects(tracks)
        elif isinstance(observable, AbstractTrackArmState):
            if observable.is_armed:
                self.connect_base_track_routing()
            else:
                self.monitor_audio_track()

    def connect_base_track_routing(self):
        # type: () -> None
        self._track_proxy.audio_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._track_proxy.audio_track.input_routing.type = InputRoutingTypeEnum.NO_INPUT
        self._track_proxy.base_track.output_routing.track = self._track_proxy.audio_track

    def monitor_audio_track(self):
        # type: () -> None
        """Restore the current monitoring state of the track"""
        try:
            self._track_proxy.audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        except ArgumentError:
            pass

    @subject_slot_group("name")
    @defer
    def _name_listener(self, _):
        # type: (Live.Track.Track) -> None
        """on any name change, cut the link"""
        self.disconnect()

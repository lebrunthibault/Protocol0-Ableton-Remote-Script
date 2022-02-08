from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAddedEvent import SimpleDummyTrackAddedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus


class SimpleDummyTrack(SimpleAudioTrack):
    KEEP_CLIPS_ON_ADDED = True

    def _added_track_init(self):
        # type: () -> None
        self.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self.input_routing.type = InputRoutingTypeEnum.NO_INPUT
        super(SimpleDummyTrack, self)._added_track_init()
        DomainEventBus.notify(SimpleDummyTrackAddedEvent(self))

    @property
    def computed_base_name(self):
        # type: () -> str
        return "dummy %d" % (self.abstract_group_track.dummy_tracks.index(self) + 1)

    @property
    def computed_color(self):
        # type: () -> int
        return self.group_track.color

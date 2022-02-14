from typing import List, Any, TYPE_CHECKING

from protocol0.domain.lom.clip.AudioDummyClip import AudioDummyClip
from protocol0.domain.lom.clip_slot.AudioDummyClipSlot import AudioDummyClipSlot
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAddedEvent import SimpleDummyTrackAddedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class SimpleDummyTrack(SimpleAudioTrack):
    KEEP_CLIPS_ON_ADDED = True
    CLIP_SLOT_CLASS = AudioDummyClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        self.abstract_group_track = self.abstract_group_track  # type: ExternalSynthTrack
        self.clip_slots = self.clip_slots  # type: List[AudioDummyClipSlot]

    @property
    def clips(self):
        # type: () -> List[AudioDummyClip]
        return super(SimpleDummyTrack, self).clips  # type: ignore

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

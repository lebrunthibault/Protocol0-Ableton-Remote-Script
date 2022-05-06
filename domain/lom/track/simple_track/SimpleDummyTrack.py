from typing import List, Any, cast

from protocol0.domain.lom.clip.AudioDummyClip import AudioDummyClip
from protocol0.domain.lom.clip_slot.AudioDummyClipSlot import AudioDummyClipSlot
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAddedEvent import SimpleDummyTrackAddedEvent
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAutomation import SimpleDummyTrackAutomation
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class SimpleDummyTrack(SimpleAudioTrack):
    CLIP_SLOT_CLASS = AudioDummyClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
        self.abstract_group_track = cast(ExternalSynthTrack, self.abstract_group_track)
        self.automation = SimpleDummyTrackAutomation(self._track, self._clip_slots, self.devices)

    @property
    def clip_slots(self):
        # type: () -> List[AudioDummyClipSlot]
        return cast(List[AudioDummyClipSlot], super(SimpleDummyTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioDummyClip]
        return cast(List[AudioDummyClip], super(SimpleDummyTrack, self).clips)

    def on_added(self):
        # type: () -> None
        self.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self.input_routing.type = InputRoutingTypeEnum.NO_INPUT
        super(SimpleDummyTrack, self).on_added()
        DomainEventBus.emit(SimpleDummyTrackAddedEvent(self._track))

    @property
    def computed_base_name(self):
        # type: () -> str
        return "dummy %d" % (self.abstract_group_track.dummy_tracks.index(self) + 1)

    @property
    def computed_color(self):
        # type: () -> int
        return self.group_track.color

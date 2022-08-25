from functools import partial

from typing import List, Any, cast, Optional

from protocol0.domain.lom.clip.DummyClip import DummyClip
from protocol0.domain.lom.clip_slot.DummyClipSlot import DummyClipSlot
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAddedEvent import (
    SimpleDummyTrackAddedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAutomation import (
    SimpleDummyTrackAutomation,
)
from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable


class SimpleDummyTrack(SimpleAudioTrack):
    CLIP_SLOT_CLASS = DummyClipSlot
    TRACK_NAME = "d"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)

        self._clip_slots.register_observer(self)

        self.automation = SimpleDummyTrackAutomation(self._track, self._clip_slots, self.devices)
        if self.name != self.TRACK_NAME:
            Scheduler.defer(partial(setattr, self, "name", self.TRACK_NAME))

    def update(self, observable):
        # type: (Observable) -> None
        # manually setting the has_automation attribute
        if isinstance(observable, SimpleTrackClipSlots):
            for clip in self.clips:
                clip.has_automation = len(clip.automation.get_automated_parameters(
                    self.devices.parameters
                )) != 0

    @classmethod
    def is_track_valid(cls, track):
        # type: (AbstractTrack) -> bool
        if isinstance(track, SimpleDummyTrack):
            return True

        # we don't accept specialized subclasses as we expect a non mapped class (e.g. no tail)
        return (
            type(track) == SimpleAudioTrack and not track.is_foldable and track.instrument is None
        )

    @property
    def clip_slots(self):
        # type: () -> List[DummyClipSlot]
        return cast(List[DummyClipSlot], super(SimpleDummyTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[DummyClip]
        return cast(List[DummyClip], super(SimpleDummyTrack, self).clips)

    def on_added(self):
        # type: () -> None
        self.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self.input_routing.type = InputRoutingTypeEnum.NO_INPUT
        super(SimpleDummyTrack, self).on_added()
        DomainEventBus.emit(SimpleDummyTrackAddedEvent(self._track))

    def prepare_automation_for_clip_start(self, dummy_clip):
        # type: (DummyClip) -> None
        """
            This will set automation values to equal the clip start
            It is used to prevent automation glitches when a track starts playing after silence
        """
        Logger.dev((self, dummy_clip))
        clip_parameters = dummy_clip.automation.get_automated_parameters(self.devices.parameters)

        for parameter in clip_parameters:
            envelope = dummy_clip.automation.get_envelope(parameter)
            # we don't take value_at_time(0) because we often have 2 points at zero,
            # the first one being wrong
            parameter.value = round(envelope.value_at_time(0.000001), 3)

    def reset_automation_to_default(self, scene_index, previous_scene_index):
        # type: (Optional[int], int) -> None
        """
            This will selectively reset automation parameters to their default
            if their are not present in the current clip (relative to the previous dummy clip)
            Called on each scene change and allows us to define only one dummy clip automation
            for a one shot effect instead of creating the automation for each scene
        """

        previous_clip = self.clip_slots[previous_scene_index].clip
        if previous_clip is None:
            return None

        previous_clip_parameters = previous_clip.automation.get_automated_parameters(self.devices.parameters)
        clip_parameters = []  # type: List[DeviceParameter]
        if scene_index and self.clip_slots[scene_index].clip is not None:
            clip_parameters = self.clip_slots[scene_index].clip.automation.get_automated_parameters(self.devices.parameters)

        parameters_to_reset = set(previous_clip_parameters) - set(clip_parameters)

        for parameter in parameters_to_reset:
            parameter.reset()

    @property
    def computed_color(self):
        # type: () -> int
        return self.group_track.appearance.color

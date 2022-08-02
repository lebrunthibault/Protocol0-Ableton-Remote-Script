from functools import partial

from typing import List, Type, cast

from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.observer.Observable import Observable


class SimpleAudioTailTrack(SimpleAudioTrack):
    CLIP_SLOT_CLASS = AudioTailClipSlot  # type: Type[AudioClipSlot]
    TRACK_NAME = "t"

    @property
    def clip_slots(self):
        # type: () -> List[AudioTailClipSlot]
        return cast(List[AudioTailClipSlot], super(SimpleAudioTailTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioTailClip]
        return cast(List[AudioTailClip], super(SimpleAudioTailTrack, self).clips)

    def configure(self):
        # type: () -> None
        self.name = self.TRACK_NAME
        try:
            self.input_routing.channel = InputRoutingChannelEnum.POST_FX
        except Protocol0Error:
            return

    def update(self, observable):
        # type: (Observable) -> None
        super(SimpleAudioTailTrack, self).update(observable)
        if isinstance(observable, SimpleTrackDevices):
            if len(list(self.devices)) != 0:
                Backend.client().show_warning("you cannot add a device to a tail track")
                for device in self.devices:
                    Scheduler.defer(partial(self.devices.delete, device))

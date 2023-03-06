from functools import partial

from typing import Any

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleTrackSaveStartedEvent import \
    SimpleTrackSaveStartedEvent
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.utils import volume_to_db


class MasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(MasterTrack, self).__init__(*a, **k)

        self.devices.register_observer(self)
        DomainEventBus.subscribe(SimpleTrackSaveStartedEvent, self._on_simple_track_save_started_event)

    def _on_simple_track_save_started_event(self, _):
        # type: (SimpleTrackSaveStartedEvent) -> None
        """youlean makes saving a track 10s + long"""
        youlean = self.devices.get_one_from_enum(DeviceEnum.YOULEAN)

        if youlean is not None:
            self.devices.delete(youlean)
            Backend.client().show_warning("Youlean removed")

    @property
    def muted(self):
        # type: () -> bool
        return self.volume != 0

    def mute_for(self, duration):
        # type: (int) -> None
        """
        Master track can not be muted so we set volume to 0
        duration: ms
        """
        self.volume = volume_to_db(0)
        Scheduler.wait_ms(duration, (partial(setattr, self, "volume", 0)))
        Scheduler.wait_ms(500, self._check_volume, unique=True)

    def _check_volume(self):
        # type: () -> None
        if self.volume != 0:
            Backend.client().show_warning("Master volume is not at 0 db, fixing")
            self.volume = 0

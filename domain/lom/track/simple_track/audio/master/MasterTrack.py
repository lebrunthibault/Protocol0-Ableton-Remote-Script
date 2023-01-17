from functools import partial

from typing import Optional, Any

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrackMuteToggledEvent import \
    MasterTrackMuteToggledEvent
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrackRoomEqToggledEvent import (
    MasterTrackRoomEqToggledEvent,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.utils import volume_to_db
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class MasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False
    _ROOM_EQ_WARNING_DELAY = 600

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        self._room_eq = None  # type: Optional[Device]
        super(MasterTrack, self).__init__(*a, **k)
        self.devices.register_observer(self)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, SimpleTrackDevices):
            room_eq = self.devices.get_one_from_enum(DeviceEnum.EQ_ROOM)
            if room_eq != self._room_eq:
                self._room_eq = room_eq
            DomainEventBus.emit(MasterTrackRoomEqToggledEvent())

    def toggle_room_eq(self):
        # type: () -> Optional[Sequence]
        if self.room_eq is None:
            seq = Sequence()
            seq.add(self.select)
            seq.add(partial(CommandBus.dispatch, LoadDeviceCommand(DeviceEnum.EQ_ROOM.name)))
            Scheduler.wait_ms(self._ROOM_EQ_WARNING_DELAY * 1000, self._warn_room_eq_enabled)
            return seq.done()

        self.room_eq.is_enabled = not self.room_eq.is_enabled
        DomainEventBus.emit(MasterTrackRoomEqToggledEvent())

        if self.room_eq.is_enabled:
            Scheduler.wait_ms(self._ROOM_EQ_WARNING_DELAY * 1000, self._warn_room_eq_enabled)

        return None

    @property
    def muted(self):
        # type: () -> bool
        return self.volume != 0

    def toggle_mute(self):
        # type: () -> None
        if self.muted:
            self.volume = 0
        else:
            self.volume = volume_to_db(0)

        Scheduler.defer(partial(DomainEventBus.emit, MasterTrackMuteToggledEvent()))

    def _warn_room_eq_enabled(self):
        # type: () ->  Optional
        if self.room_eq is not None and self.room_eq.is_enabled:
            Backend.client().show_warning("Room eq has been active for %s minutes" % (self._ROOM_EQ_WARNING_DELAY / 60))
            Scheduler.wait_ms(self._ROOM_EQ_WARNING_DELAY * 1000, self._warn_room_eq_enabled)

    @property
    def room_eq(self):
        # type: () -> Optional[Device]
        return self._room_eq

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

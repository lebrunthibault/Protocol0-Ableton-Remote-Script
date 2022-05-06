from functools import partial

from typing import Optional, Any

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.track.simple_track.MasterTrackRoomEqToggledEvent import MasterTrackRoomEqToggledEvent
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class MasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False

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
            return seq.done()

        self.room_eq.is_enabled = not self.room_eq.is_enabled
        return None

    @property
    def room_eq(self):
        # type: () -> Optional[Device]
        return self._room_eq
